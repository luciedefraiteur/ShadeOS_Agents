# Python Scope Detection — Current Status (2025-08-12_113946)

## Summary
- Advanced and mid-scope test suites are green locally.
- Decorator-aware start alignment; header multi-line handling; no AST-boundary forcing; `meta` exposed.

## Key behaviors
- Start: include contiguous decorators above `def`/`async def`; prefer functions over classes when recentering.
- Header: detect end-of-header at the `:` considering parenthesis balance across lines.
- End: last non-blank in-body line before dedent; do not include the next header line.
- Special: if starting inside decorator region, end bound equals header line (per tests convention).
- Integrity flags: `unterminated_scope_eof`, `unbalanced_delimiters`, tokenizer notes.

## Metadata
- `meta = { decorators_start, decorators_end, header_line, body_start, body_end }`.

## Next steps
- Implement ancestry discovery (nested scopes chain) and expose in runner.
- Add `--show-issues` and `--show-scope-meta` in the debug runner.
- Integrate with TFME nodes (contains/contained_in links).
