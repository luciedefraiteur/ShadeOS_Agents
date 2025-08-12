# Python Scope Meta v2 — Rollout (2025-08-12_134225)

## What
Introduce structured `meta` (v2):
- `entity: { kind, name }`
- `decorators: { span }`
- `header: { line, signature: { span } }`
- `body: { span, docstring: { span } | null, code: { span } | null }`

## Why
- Stable, human-readable ranges; easier consumption by tools and runners.
- Backward-compat preserved (legacy fields kept temporarily).

## Impact
- Runners updated to prefer v2 while falling back to legacy.
- Tests unaffected.

## Next
- Add ancestry chain and reflect it in `meta` and runners.
