#!/usr/bin/env python3
"""
ShadeOS Listener Autostart — zero-config launcher for terminal listener

- Detects current TTY, repo root, and starts the FIFO listener in daemon mode
- Records state in ~/.shadeos_listener.json for injector auto-discovery

Usage:
  In the terminal you want to control, just run:
    python shadeos_start_listener.py

It will print the listener status and where it wrote the state.
"""
from __future__ import annotations

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict

STATE_PATH = Path.home() / ".shadeos_listener.json"
DEFAULT_FIFO = "/tmp/shadeos_cmd.fifo"


def detect_tty() -> str:
    try:
        tty = os.readlink(f"/proc/{os.getpid()}/fd/1")
        return tty
    except Exception:
        return ""


def detect_repo_root() -> str:
    # Assume this script is in repo root
    return str(Path(__file__).resolve().parent)


def write_state(state: Dict) -> None:
    try:
        with open(STATE_PATH, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"[warn] Failed to write state {STATE_PATH}: {e}")


def main() -> int:
    repo_root = detect_repo_root()
    tty = detect_tty()
    fifo = os.environ.get("SHADEOS_FIFO", DEFAULT_FIFO)

    listener = Path(repo_root) / "shadeos_term_listener.py"
    if not listener.exists():
        print(f"[error] Listener not found at {listener}")
        return 2

    cmd = [
        sys.executable,
        str(listener),
        "--fifo", fifo,
        "--cwd", repo_root,
        "--echo",
        "--print-ready",
        "--post-ctrl-c",
        "--inject-enter",
        "--state-file", str(STATE_PATH),
    ]
    if tty.startswith("/dev/pts/"):
        cmd.extend(["--tty", tty])
    cmd.append("--daemon")

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print(f"[error] Failed to start listener: {e}")
        return e.returncode or 1

    # Give the daemon a moment to create FIFO
    time.sleep(0.2)

    state = {
        "fifo": fifo,
        "tty": tty,
        "cwd": repo_root,
        "started_at": int(time.time()),
        "pid": os.getpid(),  # launcher pid; the listener is daemonized
    }
    write_state(state)

    print("Listener started:")
    print(json.dumps(state, indent=2))
    print(f"State saved to: {STATE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
