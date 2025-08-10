#!/usr/bin/env python3
"""
ShadeOS TIOCSTI Injector — Simulate terminal input via ioctl(TIOCSTI)

WARNING: May be restricted by kernel security settings (some distros disable
TIOCSTI for unprivileged processes). Requires write permission to target TTY
and typically the same controlling user/session.

Usage examples:
  # By PID (resolve /proc/<pid>/fd/{0,1,2})
  python shadeos_tiocsti_inject.py --pid 35401 --text 'echo TIOCSTI_OK && pwd' --enter

  # By TTY path
  python shadeos_tiocsti_inject.py --tty /dev/pts/5 --text 'date' --enter
"""
from __future__ import annotations

import argparse
import os
import sys
import fcntl
import termios
from typing import Optional


def resolve_tty_from_pid(pid: int) -> str:
    for fd in (0, 1, 2):
        try:
            path = os.readlink(f"/proc/{pid}/fd/{fd}")
            if path.startswith("/dev/pts/"):
                return path
        except Exception:
            continue
    raise RuntimeError(f"No PTY found on fd 0/1/2 for PID {pid}")


def inject_tiocsti(tty_path: str, text: str, send_enter: bool = True) -> None:
    # Open the TTY for write; no need to write bytes via write(), only ioctl
    fd = os.open(tty_path, os.O_WRONLY)
    try:
        to_send = text
        if send_enter:
            to_send += "\n"
        # Send one char at a time via TIOCSTI
        for ch in to_send:
            fcntl.ioctl(fd, termios.TIOCSTI, ch)
    finally:
        os.close(fd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inject commands into a TTY via TIOCSTI")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pid", type=int, help="Target shell PID (resolve its PTY)")
    group.add_argument("--tty", type=str, help="Target TTY path (e.g., /dev/pts/5)")
    parser.add_argument("--text", type=str, required=True, help="Command text to inject")
    parser.add_argument("--enter", action="store_true", help="Append Enter (newline)")
    parser.add_argument("--dry-run", action="store_true", help="Print target and text without injecting")

    args = parser.parse_args()

    try:
        tty_path = args.tty or resolve_tty_from_pid(args.pid)
    except Exception as e:
        print(f"[error] Resolve TTY failed: {e}", file=sys.stderr)
        return 2

    if args.dry_run:
        print(f"TTY: {tty_path}")
        print(f"TEXT: {args.text!r}")
        print(f"ENTER: {args.enter}")
        return 0

    try:
        inject_tiocsti(tty_path, args.text, send_enter=args.enter)
        print(f"[ok] Injected into {tty_path}")
        return 0
    except PermissionError as e:
        print(f"[perm] Permission denied on {tty_path}: {e}", file=sys.stderr)
        return 13
    except OSError as e:
        print(f"[oserr] Injection failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[error] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
