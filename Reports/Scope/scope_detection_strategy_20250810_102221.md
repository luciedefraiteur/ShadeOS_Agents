# Scope Detection Strategy — Refinements and Fallbacks (2025-08-10 10:22:21)

## Problem recap
- Starting mid-scope (e.g., inside a Python function) leads to premature termination:
  - Pattern-based end (e.g., `^\s*return\s+`) cuts too early
  - Balanced-at-base-indent may also cut too early (e.g., 1-line result)

## Goals
- Keep fast, local heuristics for real-time chunking
- Be honest about uncertainty (mark invalid when suspicious)
- Offer a robust, short-budget fallback (LLM) when heuristics underperform

## Heuristic refinements
- prefer_balanced_end (default true for `.py`):
  - When starting mid-scope (not on start-pattern), ignore return/break/continue as end-patterns
  - Accept end only when delimiters are balanced AND indent has returned to base level
- min_scanned_lines:
  - For Python mid-scope, require at least 3 lines; otherwise mark `valid=false` and add issue `below_min_scanned_lines`
  - For other languages default to 1 (overrideable via param)
- Validation flags in `scope_boundaries`:
  - `started_on_start_pattern: bool`
  - `valid: bool`
  - `issues: string[]` (e.g., `ended_by_pattern_mid_scope`, `unbalanced_delimiters`, `below_min_scanned_lines`)

## Fallback flow (LLM, short budget)
- Trigger when `valid=false` and `include_analysis=true`
- Prompt uses a small snippet (~80 lines) starting at `start_line`
- Asks for strict `END_LINE: <number>`
- If proposed end_line > current end_line, extend boundaries and set `metadata.fallback_used='llm_guess_boundaries'`
- Provider timeouts remain short; one attempt only

## Cross-language considerations
- Python: rely on indentation + balanced delimiters
- C-like (js/ts/c/cpp): rely primarily on brace balance; `min_scanned_lines` default low (1–2)
- Generic: still return a best-effort chunk but mark `valid=false` with clear `issues` when confidence is low

## Visibility & debugging
- `debug:true` exposes per-line trace and end_reason/pattern
- Tool always returns `scope_boundaries` with `valid`/`issues` and `metadata.prefer_balanced_end`/`min_scanned_lines`/`fallback_used`

## Next
- Tighten the `min_scanned_lines` guard so balanced-at-one-line mid-scope is marked invalid and can trigger the LLM fallback when requested
- Add tests: mid-scope starts for Python and a brace-based language
