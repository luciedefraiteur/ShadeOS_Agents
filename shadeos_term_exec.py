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
from typing import Optional

RECIPES = {
    "e2e": "LLM_MODE=mock pytest -q Core/Agents/V10/tests/test_read_chunks_until_scope_e2e.py",
    "unit-fast": "pytest -q Core/Agents/V10/tests/test_specialized_tools.py",
    "all": "pytest -q",
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
    parser.add_argument("--pid", type=int, required=True, help="Target terminal process PID (shell PID)")
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

    args = parser.parse_args()

    tty_path = resolve_tty_from_pid(args.pid)
    cmd = args.cmd or RECIPES[args.recipe]
    if args.cwd:
        cmd = f"cd {args.cwd} && {cmd}"
    if args.tee_log:
        cmd = f"{cmd} |& tee -a {args.tee_log}"

    # Optional timeout wrapper (basic GNU coreutils 'timeout')
    if args.timeout_sec and args.timeout_sec > 0:
        cmd = f"timeout {args.timeout_sec}s {cmd}"

    if args.dry_run:
        print(f"Resolved PTY: {tty_path}")
        print(f"Command: {cmd}")
        return 0

    enter_char = "\r" if args.enter_cr else "\n"
    send_command_to_tty(tty_path, cmd, add_newline=True, enter_times=args.enter_times, wake=args.wake, enter_char=enter_char)
    print(f"[ok] Sent to {tty_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
