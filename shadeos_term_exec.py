#!/usr/bin/env python3
"""
shadeos_term_exec.py — Send commands to an existing terminal by PID (Linux)

Usage examples:
  # Send a pytest command to a VSCode integrated terminal PID 12345
  python shadeos_term_exec.py --pid 12345 --cmd "LLM_MODE=mock pytest -q Core/Agents/V10/tests/test_read_chunks_until_scope_e2e.py"

  # Use a built-in recipe
  python shadeos_term_exec.py --pid 12345 --recipe e2e

Notes:
- Works on Linux with PTY-based terminals (e.g., VSCode integrated terminal).
- We resolve /proc/<pid>/fd/0 to get the PTY path (e.g., /dev/pts/N) and write
  the command text followed by a newline, as if typed by the user.
- You must own the target PTY (same user) or have appropriate permissions.
- Use carefully; this will inject keystrokes into the terminal session.
"""

from __future__ import annotations

import os
import sys
import argparse
from typing import Optional, List, Tuple
import subprocess

RECIPES = {
    "e2e": "LLM_MODE=mock pytest -q Core/Agents/V10/tests/test_read_chunks_until_scope_e2e.py",
    "unit-fast": "pytest -q Core/Agents/V10/tests/test_specialized_tools.py",
    "all": "pytest -q",
    "e2e-runner": "python run_tests.py --e2e --timeout 20 --log /tmp/shadeos_e2e.log",
}


def resolve_tty_from_pid(pid: int) -> str:
    fd0 = f"/proc/{pid}/fd/0"
    try:
        target = os.readlink(fd0)
    except Exception as e:
        raise RuntimeError(f"Cannot readlink {fd0}: {e}")
    # Expect a PTY like /dev/pts/N
    if not target.startswith("/dev/pts/"):
        # Some shells may have fd0 -> 'pipe:[XXXX]'. Try /proc/<pid>/fd/1 or /proc/<pid>/fd/2
        for fd in (1, 2):
            try:
                t = os.readlink(f"/proc/{pid}/fd/{fd}")
                if t.startswith("/dev/pts/"):
                    target = t
                    break
            except Exception:
                pass
    if not target.startswith("/dev/pts/"):
        raise RuntimeError(f"PID {pid} does not have a PTY on fd 0/1/2 (got '{target}').")
    return target


def send_command_to_tty(tty_path: str, text: str, add_newline: bool = True, pre: str = "", post: str = "", enter_times: int = 1, wake: bool = False, enter_char: str = "\n") -> None:
    data = text
    if add_newline and not data.endswith("\n") and not data.endswith("\r"):
        # We will handle final enter explicitly below
        pass
    # Open the PTY for write only; requires permission.
    try:
        with open(tty_path, "w", buffering=1) as tty:
            if wake:
                # Send Ctrl-C to try to get back to prompt
                tty.write("\x03")
                tty.flush()
            if pre:
                tty.write(pre)
                if not (pre.endswith("\n") or pre.endswith("\r")):
                    tty.write(enter_char)
            tty.write(data)
            # Send enter(s)
            for _ in range(max(1 if add_newline else 0, enter_times)):
                tty.write(enter_char)
            if post:
                if not (post.endswith("\n") or post.endswith("\r")):
                    post += enter_char
                tty.write(post)
            tty.flush()
    except PermissionError as e:
        raise RuntimeError(f"Permission denied writing to {tty_path}: {e}")
    except Exception as e:
        raise RuntimeError(f"Error writing to {tty_path}: {e}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a command to an existing terminal by PID")
    parser.add_argument("--pid", type=int, help="Target terminal process PID (shell PID) for PTY fallback")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--cmd", type=str, help="Shell command to send (will append newline)")
    group.add_argument("--recipe", choices=sorted(RECIPES.keys()), help="Use a predefined command recipe")
    parser.add_argument("--dry-run", action="store_true", help="Do not send, just print resolved PTY and command")
    parser.add_argument("--cwd", type=str, help="If set, prepend 'cd <cwd> &&' before the command")
    parser.add_argument("--tee-log", type=str, help="If set, append '|& tee -a <log>' to the command")
    parser.add_argument("--enter-times", type=int, default=1, help="Number of extra newlines to send after the command")
    parser.add_argument("--wake", action="store_true", help="Send Ctrl-C before the command to return to prompt")
    parser.add_argument("--timeout-sec", type=int, help="If set, wrap the command with 'timeout <sec>s' to prevent hangs")
    parser.add_argument("--enter-cr", action="store_true", help="Use Carriage Return (\r) as enter key instead of newline")
    # tmux integration
    parser.add_argument("--tmux-pane", type=str, help="Send command to a tmux pane id (e.g., 'my:0.1')")
    parser.add_argument("--tmux-pid", type=int, help="Resolve tmux pane by PID (matches pane_pid)")
    parser.add_argument("--tmux-capture", type=int, metavar="LINES", help="Capture last N lines after sending (tmux capture-pane)")
    # FIFO listener integration
    parser.add_argument("--fifo", type=str, help="If set, write the command to this FIFO (listener must be running)")

    args = parser.parse_args()

    # Auto-detect default FIFO if not specified and no other backend was provided
    if not args.fifo and not args.tmux_pane and not args.tmux_pid and not args.pid:
        # Try state file from shadeos_start_listener.py
        state_path = os.path.expanduser("~/.shadeos_listener.json")
        default_fifo = os.environ.get("SHADEOS_FIFO", "/tmp/shadeos_cmd.fifo")
        fifo_candidate = None
        try:
            if os.path.exists(state_path):
                import json
                with open(state_path) as f:
                    state = json.load(f)
                    fifo_candidate = state.get("fifo")
        except Exception:
            fifo_candidate = None
        for candidate in (fifo_candidate, default_fifo):
            if candidate and os.path.exists(candidate):
                args.fifo = candidate
                break

    cmd = args.cmd or RECIPES[args.recipe]
    if args.cwd:
        cmd = f"cd {args.cwd} && {cmd}"
    if args.tee_log:
        cmd = f"{cmd} |& tee -a {args.tee_log}"

    # Optional timeout wrapper (basic GNU coreutils 'timeout')
    if args.timeout_sec and args.timeout_sec > 0:
        cmd = f"timeout {args.timeout_sec}s {cmd}"

    # If FIFO is requested and exists, use it (most reliable)
    if args.fifo:
        fifo_path = args.fifo
        if not os.path.exists(fifo_path):
            print(f"[error] FIFO not found: {fifo_path}")
            return 2
        if args.dry_run:
            print(f"FIFO: {fifo_path}")
            print(f"Command: {cmd}")
            return 0
        try:
            # Open FIFO for write (will block until listener opens for read)
            with open(fifo_path, 'w', buffering=1) as f:
                f.write(cmd)
                if not cmd.endswith("\n"):
                    f.write("\n")
                f.flush()
            print(f"[ok] Sent to FIFO {fifo_path}")
            return 0
        except Exception as e:
            print(f"[warn] FIFO write failed ({e}); trying other backends")

    # If tmux is requested, send via tmux backend
    if args.tmux_pane or args.tmux_pid:
        try:
            pane = args.tmux_pane or tmux_find_pane_by_pid(args.tmux_pid)
            if args.dry_run:
                print(f"tmux target pane: {pane}")
                print(f"Command: {cmd}")
                return 0
            tmux_send_keys(pane, cmd)
            print(f"[ok] Sent to tmux pane {pane}")
            if args.tmux_capture and args.tmux_capture > 0:
                out = tmux_capture(pane, args.tmux_capture)
                if out:
                    print(out)
            return 0
        except Exception as e:
            print(f"[warn] tmux send failed ({e}); falling back to PTY if available")

    # Fallback to PTY injection
    if not args.pid:
        print("[error] --pid is required for PTY fallback; provide --fifo or --tmux-* instead")
        return 2
    tty_path = resolve_tty_from_pid(args.pid)
    if args.dry_run:
        print(f"Resolved PTY: {tty_path}")
        print(f"Command: {cmd}")
        return 0
    enter_char = "\r" if args.enter_cr else "\n"
    send_command_to_tty(tty_path, cmd, add_newline=True, enter_times=args.enter_times, wake=args.wake, enter_char=enter_char)
    print(f"[ok] Sent to {tty_path}")
    return 0


def tmux_find_pane_by_pid(pid: int) -> str:
    """Return tmux pane id for a given pane_pid, raises if not found."""
    if not pid:
        raise RuntimeError("tmux PID is required")
    fmt = '#{session_name}:#{window_index}.#{pane_index} #{pane_pid}'
    try:
        out = subprocess.check_output(["tmux", "list-panes", "-a", "-F", fmt], text=True)
    except Exception as e:
        raise RuntimeError(f"tmux not available or list-panes failed: {e}")
    for line in out.splitlines():
        parts = line.strip().split()
        if len(parts) != 2:
            continue
        pane_id, pane_pid = parts
        try:
            if int(pane_pid) == int(pid):
                return pane_id
        except ValueError:
            continue
    raise RuntimeError(f"No tmux pane found for PID {pid}")


def tmux_send_keys(pane: str, command: str) -> None:
    """Send command + Enter to tmux pane."""
    subprocess.check_call(["tmux", "send-keys", "-t", pane, command, "Enter"]) 


def tmux_capture(pane: str, lines: int) -> str:
    """Capture last N lines from tmux pane."""
    start = f"-{int(lines)}"
    out = subprocess.check_output(["tmux", "capture-pane", "-t", pane, "-p", "-S", start], text=True)
    return out


if __name__ == "__main__":
    sys.exit(main())
