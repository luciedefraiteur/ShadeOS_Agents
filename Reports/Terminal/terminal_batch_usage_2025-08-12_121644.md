# Terminal Listener — Batch Testing Usage (2025-08-12_121644)

## Launch
- Listener (foreground): see `Reports/Terminal/terminal_injection_usage_2025-08-11_120219.md`.

## Batch runners
- Small batch: `python Core/Agents/V10/tests/debug_scope_batch.py`
- Big batch: `python Core/Agents/V10/tests/debug_scope_batch_big.py`

## Visual cues
- Start: “/!\ TESTS COMMENCENT ICI /!\”
- End: “/!\ TESTS TERMINÉS /!\” with summary
- Per test: index, name, note, file, query line, scope bounds, meta (decorators/header/signature/docstring/body_executable/body), issues, AST notes, preview with line numbers.
