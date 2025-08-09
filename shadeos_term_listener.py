#!/usr/bin/env python3
"""
ShadeOS Terminal Listener — Reliable command executor via FIFO

Usage (in your target terminal):
  # Start listener (default FIFO /tmp/shadeos_cmd.fifo)
  python shadeos_term_listener.py --fifo /tmp/shadeos_cmd.fifo --cwd /home/luciedefraiteur/ShadeOS_Agents --echo --log /tmp/shadeos_listener.log

Daemonized seamless mode (keeps your terminal free and preserves scrolling):
  TTY=$(readlink /proc/$$/fd/1)
  python shadeos_term_listener.py --fifo /tmp/shadeos_cmd.fifo \
    --cwd /home/luciedefraiteur/ShadeOS_Agents --tty "$TTY" --daemon --echo --print-ready

Then, from another process, send commands with the injector:
  python shadeos_term_exec.py --fifo /tmp/shadeos_cmd.fifo --cmd 'python run_tests.py --e2e --timeout 20 --log /tmp/shadeos_e2e.log'

This avoids brittle PTY CR/LF issues and preserves terminal UX.
"""
from __future__ import annotations

import argparse
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional
import time

DONE_MARK = "__DONE__"


def ensure_fifo(path: Path) -> None:
    if path.exists():
        # If it's a regular file, refuse
        if not path.is_fifo():
            raise RuntimeError(f"Path exists and is not a FIFO: {path}")
        return
    # Create directory if needed
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.mkfifo(path)
    except FileExistsError:
        pass


def _write_to_tty(tty: Optional[Path], text: str) -> None:
    if not text:
        return
    if tty:
        try:
            with tty.open("a", buffering=1) as tf:
                tf.write(text)
                if not text.endswith("\n"):
                    tf.write("\n")
        except Exception:
            pass
    else:
        # Fallback to stdout
        print(text)


def run_command(cmd: str, cwd: Optional[Path], env: dict, echo: bool, log: Optional[Path], tty: Optional[Path], post_ctrl_c: bool) -> int:
    if echo:
        _write_to_tty(tty, f"$ {cmd}")
    try:
        proc = subprocess.run(
            ["bash", "-lc", cmd],
            cwd=str(cwd) if cwd else None,
            env=env,
            text=True,
            capture_output=True,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        if out:
            _write_to_tty(tty, out.rstrip("\n"))
        rc = proc.returncode
    except Exception as e:
        _write_to_tty(tty, f"[error] execution failed: {e}")
        rc = 127
    if log:
        try:
            with log.open("a", buffering=1) as lf:
                lf.write(f"\n[{DONE_MARK}] rc={rc} cmd={cmd}\n")
        except Exception:
            pass
    _write_to_tty(tty, f"{DONE_MARK} rc={rc}")
    if post_ctrl_c and tty:
        try:
            with tty.open("a", buffering=1) as tf:
                tf.write("\x03\n")
                tf.flush()
        except Exception:
            pass
    return rc


def main() -> int:
    parser = argparse.ArgumentParser(description="ShadeOS terminal FIFO listener")
    parser.add_argument("--fifo", default="/tmp/shadeos_cmd.fifo", help="FIFO path to listen on")
    parser.add_argument("--cwd", help="Working directory to execute commands in")
    parser.add_argument("--echo", action="store_true", help="Echo commands before executing")
    parser.add_argument("--log", help="Append done markers to a log file")
    parser.add_argument("--tty", help="Target TTY path to mirror outputs (preserves terminal scroll)")
    parser.add_argument("--daemon", action="store_true", help="Detach and run in background (keep terminal free)")
    parser.add_argument("--print-ready", action="store_true", help="Print READY when listener is active")
    parser.add_argument("--post-ctrl-c", action="store_true", help="Send Ctrl-C to TTY after each command to restore prompt")

    args = parser.parse_args()

    fifo_path = Path(args.fifo)
    ensure_fifo(fifo_path)

    exec_cwd = Path(args.cwd).resolve() if args.cwd else None
    if exec_cwd and not exec_cwd.exists():
        print(f"[warn] cwd does not exist: {exec_cwd}")
        exec_cwd = None

    log_path = Path(args.log).resolve() if args.log else None
    tty_path = Path(args.tty).resolve() if args.tty else None

    # Prepare environment (inherit + minimal helpful defaults)
    env = os.environ.copy()
    if exec_cwd:
        env.setdefault("PYTHONPATH", f"{exec_cwd}:{env.get('PYTHONPATH','')}")

    def _announce_ready():
        if args.print_ready:
            _write_to_tty(tty_path, "READY")
        _write_to_tty(tty_path, f"Listening on FIFO: {fifo_path}")
        if exec_cwd:
            _write_to_tty(tty_path, f"Working directory: {exec_cwd}")

    # Daemonize if requested
    if args.daemon:
        pid = os.fork()
        if pid > 0:
            # Parent exits
            return 0
        # Child continues
        os.setsid()
        # Optional second fork not strictly necessary here
        # Redirect stdio to /dev/null
        devnull = os.open(os.devnull, os.O_RDWR)
        os.dup2(devnull, 0)
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        try:
            os.close(devnull)
        except Exception:
            pass
        # announce via TTY
        _announce_ready()
    else:
        _announce_ready()

    # Persistent loop: reopen FIFO after writers disconnect
    try:
        while True:
            with open(fifo_path, "r") as f:
                for line in f:
                    cmd = line.rstrip("\r\n")
                    if not cmd:
                        continue
                    run_command(cmd, exec_cwd, env, args.echo, log_path, tty_path, args.post_ctrl_c)
                # Writer closed; loop to reopen
    except KeyboardInterrupt:
        _write_to_tty(tty_path, "[info] Listener stopped (Ctrl-C)")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
