# Python Scope Detection — Advanced Test Matrix (2025-08-11_140149)

## Goals
Stress the scope detector with realistic, tricky Python patterns before enabling nested recursive ancestry.

## Areas to cover
1) Complex decorators
- Stacked decorators (3-4), with calls and kwargs, multi-line
- `@property`, `@classmethod`, `@staticmethod`, mixed with return annotations
- Expectation: start includes all contiguous decorators; end at method dedent

2) Multi-line signatures
- Params across 3-5 lines, with `*args`, `**kwargs`, annotations, defaults, trailing comma
- Expectation: start at `def`, end at dedent; no premature cut by internal returns

3) Docstrings edge cases
- Triple-quoted with embedded quotes/backslashes; leading/trailing blank lines
- Comments between header and first body line
- Expectation: first body line recognized after docstring/comments; end correct

4) Dense control flow
- Long `if/elif/else` chains, `try/except/else/finally`, nested `with`
- Internal `return/break/continue/raise` spread
- Expectation: end only on dedent

5) Async and pattern matching
- `async def` with `await`; `match/case` (Py 3.10+) with multiple `case`, `case _`
- Expectation: unchanged indent-based behavior

6) Non-trivial nesting (pre-recursive)
- Class with decorated methods, inner class, nested function inside a method
- Expectation: correct ranges for each level before ancestry mode

7) Continuations/parentheses
- Expressions spanning lines via `()[]{}` and `\` continuation
- Expectation: not affecting end (still dedent), no unbalanced outside strings

8) Strings/f-strings pitfalls
- f-strings with `{{ }}`, `=`, `!r/!s`, nested formatting
- Unterminated strings (intentional corruption)
- Expectation: flag `unterminated_string` in snippet; tool remains non-blocking

9) File/format edges
- EOF without newline, CRLF mix, mixed tabs/spaces in indentation
- Expectation: flags like `unterminated_scope_eof`, optionally `tab_space_mixed`; AST notes allowed

10) Large files/perf
- 5–10k lines; long function followed by many top-level blocks
- Expectation: correct bounds; reasonable runtime

11) Anti-code inside triple quotes
- Fake `def/class` inside docstrings/comments
- Expectation: no recenter on fake headers

12) Property-based (optional)
- Generate variations of headers/decorators/branches
- Invariant: end = last in-body non-blank line (indent > header), start <= end

## Tooling
- Fixtures under `Core/Agents/V10/tests/fixtures/advanced/`
- Tests `test_scope_advanced_*.py` with explicit assertions
- Golden tests: compare bounds to `ast end_lineno` for clean functions/classes (when available)
- Debug runner: add `--show-issues` to print `issues` and `ast_notes`

## Exit criteria
- All advanced tests green locally
- Debug runner outputs match expectations
- Ready to implement nested recursive ancestry discovery
