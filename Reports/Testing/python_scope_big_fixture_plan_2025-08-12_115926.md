# Python Scope — Big Fixture Plan (2025-08-12_115926)

## Goal
Design a single comprehensive Python file that covers most tricky patterns, and run multiple queries at various lines (headers, mid-decorators, mid-body, after returns, EOF edges).

## Structure of the big fixture
1) Top-level imports and comments
2) Class `Alpha` with:
   - stacked decorators on a method
   - a method with multi-line signature and docstring
   - inner class `Inner` with a nested function
3) Standalone functions:
   - `beta`: dense control flow + try/except/finally
   - `gamma`: line continuations and f-strings
   - `delta`: async with match/case
4) Edge cases:
   - unterminated string function (flag expected)
   - function near EOF without dedent (unterminated_scope_eof)

## Query matrix
- For each scope, run 3–5 queries:
  - on a decorator line (if any)
  - on header line
  - mid-signature (if multi-line)
  - inside docstring (if any)
  - inside body (various offsets)
  - right after last body line (should not include next header)

## Runner updates
- Add `debug_scope_batch_big.py` to iterate the matrix and print the same meta/anchors/preview with visible start/stop markers.
- Allow filtering by case name/pattern via CLI args.
