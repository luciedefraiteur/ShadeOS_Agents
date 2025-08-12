# Python Code/Scope Corruption Detection Strategy (2025-08-11_121604)

## Purpose
Define a deterministic, parser-free (or stdlib-only) strategy to detect corrupted Python files/scopes before/after scope boundary detection, with actionable issue flags. LLM optional for repair suggestions, not required for detection.

## Signals and how to detect them
- unterminated_string / unterminated_triple_quote
  - Use `tokenize.generate_tokens` on the text (file or scope). Catch `tokenize.TokenError` (e.g., "EOL while scanning string literal").
  - Maintain a simple quote-state automaton if needed (handles escapes) to corroborate and locate region.
- invalid_syntax_ast
  - Use `ast.parse(text)` on the full file; for a scope snippet, first try raw parse; if it fails, try wrapping as a function body (`def __wrap__():\n` + indented snippet). If wrap parses, flag `partial_snippet_wrapped_ok` instead of syntax error.
- indent_inconsistent / tab_space_mixed
  - Build an indent stack from leading whitespace of non-blank, non-comment lines. Each indent must be either tabs-only or spaces-only; mixing per-file or switching width mid-level yields flags.
  - A dedent must match a previous indent level; otherwise, inconsistent dedent.
- unbalanced_delimiters / unbalanced_delimiters_scope
  - Track (), [], {} outside of strings/comments. Non-zero at end ⇒ unbalanced.
- unterminated_scope_eof
  - For Python, when a scope is started but no dedent to start indent occurs before EOF.
- mixed_newlines / nul_byte / encoding
  - Scan file bytes for `\r\n` vs `\n` mix, NUL byte, and decode errors.

## Policy
- File-level preflight (before scope detection):
  - Run tokenizer and `ast.parse` on full text; collect high-confidence issues (encoding, tabs/spaces mix, unbalanced at file end, mixed newlines).
  - If fatal (e.g., cannot decode file), abort with `success=False`.
- Scope-level validation (after [start,end] found):
  - Re-run tokenizer on the slice; if token errors or unbalanced delimiters ⇒ `valid=False` and add issues.
  - If EOF without dedent ⇒ `unterminated_scope_eof`.
- Return best-effort ranges and content even when `valid=False`, so downstream tools/tests can inspect.

## Why algorithmic is enough (for Python)
- Indentation + stdlib `tokenize` and `ast` cover most real-world corruptions deterministically.
- LLM is optional for human-like repairs/patch proposals or when dealing with highly obfuscated snippets.

## Integration plan
1) Implement `_preflight_python_integrity(text)` returning `{issues: [], notes: []}` with checks above.
2) Call preflight at file-load time; surface `file_issues` in tool metadata.
3) After detecting scope `[start,end]`, run `_validate_scope_snippet(text[start-1:end])`; merge into `scope_boundaries.issues` and propagate `valid=False` if any fatal.
4) Extend debug runner to print issues clearly; add a `--show-file-issues` option.

## Test fixtures (to cover)
- Strings: missing closing quotes, triple-quoted docstrings, nested quotes with escapes.
- Indentation: inconsistent dedents, tab/space mixes, block without closing dedent before EOF.
- Control flow: internal returns, try/except/finally; ensure no premature cut.
- Multiline signatures and decorators: ensure header detection robust with decorators and folded params.

## Optional LLM usage
- When `issues` include `unterminated_string` or `indent_inconsistent`, an LLM can propose a fix patch; keep it behind a feature flag, never blocking detection.
