# Terminal Injection for Efficient E2E Testing — Reasoning & Workflow

## Summary of options
- TIOCSTI (ioctl): strongest "type like keyboard" but often blocked (kernel hardening, VSCode). Keep for lab-only.
- /dev/pts write: prints text, does not push into shell input.
- tmux send-keys: reliable if tmux is used; can affect UX (scroll, capture) unless carefully handled.
- VSCode extension API (Terminal.sendText): cleanest cross‑platform way if we can create/control the terminal.
- FIFO listener: robust, editor-agnostic, preserves user UX if we mirror to original TTY and daemonize.

## Chosen approach (now)
- Use a FIFO-based listener (`shadeos_term_listener.py`) launched once in the user terminal (or via `shadeos_start_listener.py`).
- Injector (`shadeos_term_exec.py`) writes commands into the FIFO; listener runs them via `bash -lc`.
- Mirror outputs to original TTY, keep terminal usable; optional Ctrl‑C and newline injection to restore prompt.
- Auto-discovery via `~/.shadeos_listener.json` (started by `shadeos_start_listener.py`) so the injector needs no extra flags.

## Why this balances reliability & UX
- No dependence on CR/LF peculiarities of integrated terminals.
- No kernel-level hacks; works on modern distros without elevated privileges.
- Keeps scrolling and prompt; user can keep typing.
- Still allows free-form commands; not locked to recipes.

## Next step (nice-to-have)
- Small VSCode extension to create a named terminal ("ShadeOS Tests") and sendText for mock E2E and real LLM E2E variants.
- Mark real LLM E2E as opt-in with short provider timeouts and a single retry.

## Test strategy: fast by default, LLM on-demand
- Default tests run in mock mode (fast, deterministic, short timeouts).
- Separate E2E LLM spec (Gemini): short HTTP timeout (~10s), one retry on 429, total suite budget ~45s.
- Clear commands to run both paths.

## Commands
- Start listener (zero-config):
  - `python shadeos_start_listener.py`
- Inject a quick E2E run:
  - `python shadeos_term_exec.py --cmd 'python run_tests.py --e2e --timeout 20 --log /tmp/shadeos_e2e.log'`
- View log:
  - `tail -f /tmp/shadeos_e2e.log`
