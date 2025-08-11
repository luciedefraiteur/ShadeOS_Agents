# Python Scope Detection for Vibe Coding — Relevance-first Integration (2025-08-11_130039)

## Intent
Optimize scope detection for a developer’s live workflow (Vibe Coding): fast, relevant, non-blocking diagnostics, and immediate memory integration for the Dev Agent (V10) via TemporalFractalMemoryEngine.

## Core principles
- No heavy repairs in detection path: if a snippet is corrupted, flag it; do not attempt to “fix” via wrapping or LLM in this pass.
- Deterministic, low-latency: indentation + tokenize checks. AST parse optional for note-level signals only; never blocks or mutates ranges.
- Relevance-first output: concise boundaries, corruption flags, and a summary tailored for the Dev Agent.

## Detection pipeline
1) Heuristic boundaries (indentation-based) — as implemented.
2) Integrity check (lightweight):
   - Tokenize snippet: if TokenError ⇒ `issues += ['unterminated_string']`.
   - Delimiters ()[]{} balance outside strings/comments; if non-zero ⇒ `issues += ['unbalanced_delimiters_scope']`.
   - EOF without dedent ⇒ `issues += ['unterminated_scope_eof']`.
   - Optionally `ast.parse` as NOTES only (no wrapping). If fails ⇒ `notes += ['ast_invalid_snippet']` (no mutation, no fallback).
3) Do not wrap snippets; never change the output to make it parsable.

## Memory integration (TFME)
- For each detected scope, create a temporal node with:
  - content: scope text (possibly truncated for size policies)
  - metadata: `file_path`, `start_line`, `end_line`, `indent_level`, `issues[]`, `summary`, `hash`
  - Linkage: chain to previous/next scopes; link to parent scope (once ancestry is available) as `contains/contained_in`.
- Flagged scopes (corrupted) are explicitly marked so the Dev Agent can prioritize or suggest fixes.
- Provide a short ‘vibe summary’ per scope node: kind (class/def/unknown), estimated intent (based on header), and issue hints.

## Dev Agent (V10) consumption
- The Dev Agent reads the latest temporal nodes for the current file and focuses on nodes with issues or high activity.
- Operations:
  - Highlight problematic scopes (unterminated strings, EOF without dedent).
  - Offer quick actions (close quotes, normalize indent) as suggestions (separate tool), not in the detector.

## Why no dummy wrapper
- Wrapping hides real corruption and may mislead the agent about the true state. In vibe coding, visibility of the broken state is essential.
- AST validation remains as a note for the agent, not a fixer.

## Next steps
- Remove snippet wrapping path; keep tokenize-only and unbalanced checks.
- Emit `vibe_summary` and `issues` in the tool’s output; ensure TFME node metadata includes them.
- Implement ancestry discovery to create `contains/contained_in` links.
