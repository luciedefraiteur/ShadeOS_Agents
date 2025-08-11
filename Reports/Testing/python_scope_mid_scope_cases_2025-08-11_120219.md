# Python Scope Detection — Mid-Scope Heavy Cases (2025-08-11)

## Goals
- Validate detection when starting mid-scope in dense/ugly code (deep nesting, blank lines, comments, docstrings, mixed control flow).
- Validate behavior on intentionally incorrect/unterminated scopes (no dedent before EOF).

## Planned cases
1) mid-scope inside nested function:
   - File: fixtures/nested_heavy.py
   - Start at inner `for` body (not on `def`), expect detection to shift start to `def` and end at the correct dedent.
2) mid-scope inside class method with decorators and docstring:
   - File: fixtures/decorated_docstring.py
   - Start at a line inside the method, expect start recentered to decorators+def header; end at method dedent.
3) mid-scope in complex control flow (elif/else/try/finally):
   - File: fixtures/control_heavy.py
   - Start inside `elif`, ensure end is not cut on internal `return`.
4) intentionally incorrect: unterminated scope at EOF:
   - File: fixtures/unterminated.py
   - Start on a `def` near EOF with no dedent; expect `issues` includes `unterminated_scope_eof` and `valid=False`.

## Assertions
- Ranges [start,end] match manual expectations; `valid` is False for unterminated.
- When starting mid-scope, `started_on_start_pattern=True` is expected after start shift; `scanned_lines`>=min window.
- Debug trace contains `eof_without_dedent` note for case 4.
