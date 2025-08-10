# read_chunks_until_scope — Diagnostic (2025-08-09)

## Command executed
```
python shadeos_cli.py exec-tool --tool read_chunks_until_scope --params-json '{"file_path":"Core/Agents/V10/specialized_tools.py","start_line":860,"include_analysis":false,"debug":true}'
```

## Observed output (key parts)
- success: true
- scope_boundaries:
  - start_line: 860
  - end_line: 862
  - scanned_lines: 3
  - end_reason: pattern
  - end_pattern: ^\s*return\s+
  - debug_trace (3 entries): shows indent/brackets/braces/parens evolution; match on line 862 (return)
- scope_content preview: snippet ending at `return 0` (function `_calculate_indent_level`)

## Interpretation
- The tool started at line 860 (inside `_calculate_indent_level`), scanned 3 lines, and ended the scope on a `return` line according to `end_patterns`. This is consistent with current heuristics:
  - For `auto`, `end_patterns` includes `^\s*return\s+` which may be too aggressive when starting in the middle of a function.
- When starting mid-function, a premature `return` can prematurely terminate the "scope" read, instead of reading until the true end of the function/class/block.

## Current limitations
- Heuristics are conservative and may cut at early `return` when `start_line` points inside a function.
- No upward scan to detect the start of the enclosing scope; only forward scan from `start_line`.

## Recommendations
- Improve scope detection when starting mid-scope:
  - Option A (quick): if `scope_type` is `function`, ignore `return` as hard end; rely on indentation balance (Python) or brace balance (C-like languages).
  - Option B (better): perform a quick backward scan to find the nearest start pattern (`def`, `class`, `{`, etc.), then forward scan from there.
  - Option C: add a `stop_on_return` boolean param (default false); for `auto`, disable `return`-based cutting unless `start_line` is exactly on a start pattern.
- Expose a flag `prefer_balanced_end=true` to force ending only when bracket/brace/paren counters return to baseline.

## Next steps
- Implement `prefer_balanced_end` default true for Python files; keep `end_patterns` as additional hints only if starting at a start-pattern line.
- Add tests for mid-function starts to avoid premature cuts.
