# Python Scope Detection — Progress Update (2025-08-11_161324)

## What changed
- Heuristic refined (Python):
  - Start recentering: first contiguous decorator(s) above `def` or header line itself
  - End: inclusive on last in-body line (indent > header)
  - EOF without dedent: `unterminated_scope_eof` flagged on heuristic snippet
- AST validation (notes only): `ast_invalid_snippet` in `ast_notes` — no wrapping, no mutation of ranges
- AST refinement (optional): when a clean AST node covers the query line, we can align ranges to `node.lineno..node.end_lineno` while preserving integrity flags from the heuristic pass

## Open design question
- Split decorators vs scope body:
  - Proposal: return `decorators: [start_line, end_line]` alongside `header_line` and `body: [start,end]`
  - Benefits: downstream tools can display decorators separately and reason about them without conflating with body
  - Plan: introduce `scope_meta` structure: `{decorators_start, decorators_end, header_line, body_start, body_end}`

## Tests status
- Mid-scope heavy suite: green (4/4) with indentation-only end and recentering
- Advanced suite: initial failures due to strict line expectations; plan is to:
  - Normalize fixtures (explicit blank lines to anchor decorator lines)
  - Harmonize assertions with final convention (start: first decorator/header; end: last in-body line)
  - Keep integrity flags from heuristic regardless of AST success

## Next steps
1) Implement `scope_meta` with separate decorator range and body range
2) Adjust advanced fixtures and tests to the final convention
3) Ensure EOF/unterminated flags persist even if AST of the full file parses
4) Extend runner with `--show-issues` and `--show-scope-meta`
5) Prepare nested recursive ancestry (enclosing scopes chain), then TFME node creation with links (contains/contained_in)
