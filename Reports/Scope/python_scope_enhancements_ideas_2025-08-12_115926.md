# Python Scope — Enhancement Ideas (2025-08-12_115926)

## New meta segmentation
- decorators: [start,end]
- header_line: int
- header_signature: [start,end] — lines from header start until the colon `:` (including continuations and annotations)
- header_trailing_comments: [start,end] — inline/trailing comments right after the signature (optional)
- body_docstring: [start,end] — if first body statement is a docstring
- body_executable: [start,end] — body excluding docstring/comments leading block

## Rationale
- Enable precise highlighting of signature vs executable content.
- Support tools that render structure-aware previews and enable quick navigation (e.g., jump to signature, docstring, first statement).

## Detection approach
- Re-use existing header end detection (`:` with balanced parentheses) to set `header_signature` end.
- If first in-body node is a string literal on its own line, treat as `body_docstring` until its closing line.
- `body_executable` starts after docstring/comments block; otherwise equals body range.

## Naming considerations
- `header_signature` clear vs current `header_line`.
- `body_executable` more explicit than `body`.

## Output format (example)
```
meta = {
  decorators_start, decorators_end,
  header_line,
  header_signature: [h_start, h_end],
  body_docstring: [d_start, d_end],
  body_executable: [b_start, b_end],
}
```

## Test updates
- Extend advanced fixtures to assert signature/docstring partitioning where applicable.
- Update runner to show these ranges with anchors.
