# Terminal Command Injection Strategy (2025-08-09)

## Context
- PTY-based injection (writing to /dev/pts/N) can fail to execute commands in some integrated terminals (e.g., VSCode), due to bracketed paste mode, CR/LF handling, or restricted TIOCSTI.
- Symptom observed: command text appears, cursor returns to start of line, no execution on Enter.

## Proposal
- Introduce a robust two-tier injection approach:

1) Terminal-side Listener (preferred)
- A small one-time “server” script run by the user inside the target terminal:
  - Creates a named pipe (FIFO) or UNIX domain socket (e.g., /tmp/shadeos_cmd.fifo)
  - Loops reading commands and executes them via `bash -lc "<cmd>"`, echoing results and a delimiter (e.g., `__DONE__`).
- Pros: Reliable execution, no dependency on terminal CR/LF quirks, easy log capture
- Cons: Requires launching the listener once per terminal session

2) Fallback Injectors
- PTY writer (current `shadeos_term_exec.py`) with
  - explicit Enter handling (LF/CR), wake (Ctrl-C), multiple Enters
  - optional `cd`, timeout wrapper, and `tee` logging
- Optional tmux/screen backend when present: `tmux send-keys`/`screen -X stuff`

## Implementation Plan
- Add `shadeos_term_server.py`:
  - `--fifo /tmp/shadeos_cmd.fifo` (default path)
  - Prints prompt and consumes commands until EOF; each command executed via `bash -lc` and delimited with `__DONE__`
- Extend `shadeos_term_exec.py`:
  - If `--fifo` provided and exists: write the command into FIFO instead of PTY
  - Else fallback to current PTY injection
- Optional: `--tmux-pane` to send to an identified tmux pane

## Rationale
- Matches reliability of tools like Augment by avoiding brittle CR/LF/PTTY behavior
- Keeps PTY method for cases where FIFO/server is not possible
- Simple to adopt: users start the listener once per terminal and then all commands are injected reliably
