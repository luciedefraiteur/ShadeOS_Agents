# Python Scope — Meta Reference (2025-08-12_121644)

## Meta fields
- decorators_start, decorators_end: inclusive range of decorators (comments/blank tolerated between decorators).
- header_line: line number of `def`/`async def`/`class` header.
- header_signature: [start,end] signature lines (until the `:`), including continuations and annotations.
- body_start, body_end: inclusive range of the scope body.
- body_docstring: [start,end] if first body statement is a docstring; otherwise omitted.
- body_executable: [start,end] body excluding the initial docstring/comments.

## Policy
- Start aligns to decorators group for functions/methods.
- End is last non-blank in-body line before dedent.
- EOF without dedent => `unterminated_scope_eof` issue surfaced.

## Notes
- AST validation is notes-only; no boundary forcing.
