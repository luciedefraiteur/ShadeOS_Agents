# Python Scope Detection Abstraction (2025-08-11)

## Goal
Reliable detection of Python scope boundaries starting from an arbitrary line, with correct inclusion of the scope body and exclusion of the following scope/header.

## Current heuristics
- Start patterns (Python): `^\s*(def|class)\b`, also blocks like `if/for/while/try/with` for mid-scope safety.
- End patterns (Python): explicit `return|pass|raise` for function/class minimal bodies when applicable.
- Balanced-root heuristic: when scanning reaches a non-empty line at root indentation (<= base indent) with all delimiters balanced, treat it as the beginning of the next top-level block; close current scope just before it.
- Mid-scope start shift: if initial `start_line` doesn’t match a start pattern, shift `scope_start` forward to the first encountered start pattern to avoid partial leading content.
- Minimum scan window: enforce a minimum when starting mid-scope to avoid too-early termination.

## Boundaries decisions
- If end matched by explicit end pattern, include that line in the scope (e.g., `return`).
- If end matched by balanced-root non-empty, do not include this line; close at the last non-blank line seen within the scope.
- Never terminate on the same line as the detected start.

## Next steps (beyond Python)
- Braced languages (JS/Java/C): adopt explicit brace balance with start `{` and end `}` matching; similar “next top-level” heuristic.
- Mixed indentation anomalies and decorators: detect `@decorator` lines preceding `def` and include them in the start shift.

## Test anchor
Validated on `Core/Agents/V10/tests/debug_scope_source.py` with expected ranges:
- class Greeter: 5..14
- greet: 9..11
- add: 15..17
- factorial: 20..24
