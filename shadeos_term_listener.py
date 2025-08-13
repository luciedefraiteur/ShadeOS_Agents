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
from typing import Optional, List, Iterable
import json
import fcntl
import termios
import time
import signal

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


def _read_cmdline(pid: int) -> List[str]:
    """Read /proc/<pid>/cmdline and split into argv list. Returns [] on error."""
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            data = f.read()
        if not data:
            return []
        parts = data.split(b"\0")
        return [p.decode(errors="ignore") for p in parts if p]
    except Exception:
        return []


def _same_user(pid: int) -> bool:
    try:
        st = os.stat(f"/proc/{pid}")
        return st.st_uid == os.getuid()
    except Exception:
        return False


def purge_duplicate_listeners(target_fifo: Path, tty: Optional[Path]) -> int:
    """Kill other shadeos_term_listener.py processes reading the same FIFO for this user."""
    killed = 0
    target_str = str(target_fifo)
    try:
        for entry in os.scandir("/proc"):
            if not entry.is_dir() or not entry.name.isdigit():
                continue
            pid = int(entry.name)
            if pid == os.getpid():
                continue
            if not _same_user(pid):
                continue
            argv = _read_cmdline(pid)
            if not argv:
                continue
            # Match script and fifo path
            if "shadeos_term_listener.py" in " ".join(argv) and "--fifo" in argv:
                try:
                    fifo_index = argv.index("--fifo") + 1
                    fifo_value = argv[fifo_index] if fifo_index < len(argv) else ""
                except ValueError:
                    fifo_value = ""
                if fifo_value == target_str:
                    try:
                        os.kill(pid, 15)  # SIGTERM
                        killed += 1
                    except Exception:
                        pass
    except Exception:
        return killed
    # brief grace period
    time.sleep(0.2)
    if killed:
        msg = f"[info] Purged {killed} duplicate listener(s) for FIFO {target_str}"
        _write_to_tty(tty, msg)
    return killed


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


def _iter_pids_on_tty(tty: Path) -> Iterable[int]:
    """Yield PIDs that have the given TTY open on fd 0/1/2 (same user only)."""
    tty_str = str(tty)
    try:
        for entry in os.scandir("/proc"):
            if not entry.is_dir() or not entry.name.isdigit():
                continue
            pid = int(entry.name)
            if not _same_user(pid):
                continue
            # Check a few fds for the TTY
            found = False
            for fd in (0, 1, 2):
                link = f"/proc/{pid}/fd/{fd}"
                try:
                    target = os.readlink(link)
                    if target == tty_str:
                        found = True
                        break
                except Exception:
                    continue
            if found:
                yield pid
    except Exception:
        return


def _read_comm(pid: int) -> str:
    try:
        with open(f"/proc/{pid}/comm", "rt") as f:
            return f.read().strip()
    except Exception:
        return ""


def _find_shell_pids(tty: Optional[Path]) -> List[int]:
    """Return likely shell PIDs attached to the given TTY (bash/zsh/fish)."""
    if not tty:
        return []
    shells = {"bash", "zsh", "fish", "sh"}
    candidates: List[int] = []
    for pid in _iter_pids_on_tty(tty):
        comm = _read_comm(pid).lower()
        if comm in shells:
            candidates.append(pid)
    return candidates


def _send_sigint_to_shell(tty: Optional[Path]) -> None:
    for pid in _find_shell_pids(tty):
        try:
            os.kill(pid, signal.SIGINT)
        except Exception:
            pass


def run_command(cmd: str, cwd: Optional[Path], env: dict, echo: bool, log: Optional[Path], tty: Optional[Path], post_ctrl_c: bool, inject_enter: bool, post_sigint: bool) -> int:
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
            if log:
                try:
                    with log.open("a", buffering=1) as lf:
                        lf.write(out)
                        if not out.endswith("\n"):
                            lf.write("\n")
                except Exception:
                    pass
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
    if inject_enter and tty:
        try:
            fd = os.open(str(tty), os.O_WRONLY)
            try:
                fcntl.ioctl(fd, termios.TIOCSTI, "\n")
            finally:
                os.close(fd)
        except Exception:
            pass
    if post_sigint:
        _send_sigint_to_shell(tty)
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
    parser.add_argument("--inject-enter", action="store_true", help="Try ioctl(TIOCSTI) to push Enter into shell input (if allowed)")
    parser.add_argument("--state-file", help="Write listener state (pid, fifo, tty, cwd, log) to this JSON file")
    parser.add_argument("--post-sigint", action="store_true", help="Send a real SIGINT to the shell on the target TTY after each command (restores prompt even in daemon mode)")

    args = parser.parse_args()

    fifo_path = Path(args.fifo)
    # Purge duplicate listeners bound to the same FIFO (same user)
    # Do this before opening/creating the FIFO to avoid racing multiple readers
    tty_path = Path(args.tty).resolve() if args.tty else None
    try:
        purge_duplicate_listeners(fifo_path, tty_path)
    except Exception:
        # Non-fatal; continue listener startup
        pass
    ensure_fifo(fifo_path)

    exec_cwd = Path(args.cwd).resolve() if args.cwd else None
    if exec_cwd and not exec_cwd.exists():
        print(f"[warn] cwd does not exist: {exec_cwd}")
        exec_cwd = None

    log_path = Path(args.log).resolve() if args.log else None

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
        # Persist state if requested
        if args.state_file:
            try:
                state = {
                    'listener_pid': os.getpid(),
                    'fifo': str(fifo_path),
                    'tty': str(tty_path) if tty_path else None,
                    'cwd': str(exec_cwd) if exec_cwd else None,
                    'log': str(log_path) if log_path else None,
                    'started_at': int(time.time()),
                }
                with open(args.state_file, 'w') as sf:
                    json.dump(state, sf, indent=2)
            except Exception:
                pass

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
                    run_command(cmd, exec_cwd, env, args.echo, log_path, tty_path, args.post_ctrl_c, args.inject_enter, args.post_sigint)
                # Writer closed; loop to reopen
    except KeyboardInterrupt:
        _write_to_tty(tty_path, "[info] Listener stopped (Ctrl-C)")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
