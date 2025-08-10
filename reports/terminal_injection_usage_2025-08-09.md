# Terminal Injection — Usage Cheatsheet and Current Progress (2025-08-09)

## Listener (start once in the target terminal)
- Recommended one-liner (zero-config):
  - `python shadeos_start_listener.py`
- What it does:
  - Starts `shadeos_term_listener.py` in daemon mode (terminal stays free).
  - Restores prompt after each command (Ctrl-C + optional Enter injection).
  - Writes state file for auto-discovery: `~/.shadeos_listener.json` (fifo, tty, cwd, log).

## Injector (send any command, auto-discovers listener)
- Free-form command:
  - `python shadeos_term_exec.py --cmd 'echo Hello && date'`
- E2E test run (mock, fast):
  - `python shadeos_term_exec.py --cmd 'python run_tests.py --e2e --timeout 20 --log /tmp/shadeos_e2e.log'`
- CLI showcase (read_chunks_until_scope debug):
  - `python shadeos_term_exec.py --cmd "python shadeos_cli.py exec-tool --tool read_chunks_until_scope --params-json '{\"file_path\":\"Core/Agents/V10/specialized_tools.py\",\"start_line\":860,\"include_analysis\":false,\"debug\":true}' |& tee -a /tmp/shadeos_chunks_debug.log"`

Notes:
- Auto-discovery tries `~/.shadeos_listener.json` then `/tmp/shadeos_cmd.fifo`.
- Environment: the listener executes in repo root and mirrors outputs to your terminal (scroll preserved).

## Debug visibility
- `read_chunks_until_scope` supports `debug:true`:
  - `data.scope_boundaries`: now includes `scanned_lines`, `end_reason` (pattern/balanced), `end_pattern`.
  - `metadata.debug`: per-line trace (indent/brackets/braces/parens, matched_end).
- Listener can mirror command outputs into a log (foreground mode): `--log /tmp/shadeos_listener.log`.
- E2E logs typically go to `/tmp/shadeos_e2e.log` (via run_tests.py).

## Progress so far
- FIFO listener and injector implemented (daemon + auto-discovery + prompt restore).
- E2E (mock) stabilized: `3 passed` in ~0.6s.
- CLI available: `shadeos_cli.py` with `list-tools`, `exec-tool`, and `read-chunks`.
- Provider Gemini (REST) with key rotation and DI into V10 registry (auto-detects LLM mode; mock by default for tests).
- Tests are path-robust (conftest inserts repo root to `sys.path`).

## Next steps (optional)
- Add a VSCode extension to create a dedicated terminal and send commands (clean UX, no PTY hacks).
- Add an E2E LLM test suite (Gemini) opt-in with short provider timeouts and single retry.
