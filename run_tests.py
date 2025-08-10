#!/usr/bin/env python3
"""
Run ShadeOS tests reliably from any shell/terminal/IDE.

- Forces CWD to repo root
- Ensures PYTHONPATH contains repo root
- Loads ~/.shadeos_env via conftest.py implicitly
- Supports quick presets and timeout

Examples:
  python run_tests.py --e2e --timeout 20 --log /tmp/shadeos_e2e.log
  python run_tests.py --unit-fast -q
  python run_tests.py --all -k read_chunks
"""
from __future__ import annotations

import argparse
import os
import sys
import subprocess
from pathlib import Path
from typing import List


def build_pytest_command(args: argparse.Namespace, repo_root: Path) -> List[str]:
    cmd = [sys.executable, "-m", "pytest"]
    if args.quiet:
        cmd.append("-q")
    if args.pattern:
        cmd.extend(["-k", args.pattern])
    if args.e2e:
        cmd.append("Core/Agents/V10/tests/test_read_chunks_until_scope_e2e.py")
    elif args.unit_fast:
        cmd.append("Core/Agents/V10/tests/test_specialized_tools.py")
    else:
        cmd.append(".")
    return cmd


def main() -> int:
    parser = argparse.ArgumentParser(description="ShadeOS test runner")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--e2e", action="store_true", help="Run E2E tests for read_chunks_until_scope")
    group.add_argument("--unit-fast", dest="unit_fast", action="store_true", help="Run fast unit tests for specialized tools")
    group.add_argument("--all", action="store_true", help="Run all tests (default)")
    parser.add_argument("-k", "--pattern", help="Pytest -k expression filter")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds (default: 30)")
    parser.add_argument("--log", type=str, help="If set, tee output to this file")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet output (-q)")

    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    os.chdir(repo_root)

    # Ensure PYTHONPATH
    os.environ["PYTHONPATH"] = f"{repo_root}:{os.environ.get('PYTHONPATH','')}"
    # Force mock LLM for tests to avoid network/provider hangs
    os.environ["LLM_MODE"] = "mock"

    cmd = build_pytest_command(args, repo_root)

    try:
        if args.log:
            with open(args.log, "a", buffering=1) as logf:
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=args.timeout, text=True)
                logf.write(proc.stdout)
                print(proc.stdout, end="")
                return proc.returncode
        else:
            proc = subprocess.run(cmd, timeout=args.timeout)
            return proc.returncode
    except subprocess.TimeoutExpired:
        print(f"[error] Tests timed out after {args.timeout}s", file=sys.stderr)
        return 124


if __name__ == "__main__":
    raise SystemExit(main())
