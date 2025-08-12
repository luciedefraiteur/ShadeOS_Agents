# Debug Runners Update (2025-08-12_134225)

## Changes
- `debug_scope_runner.py`, `debug_scope_batch.py`, `debug_scope_batch_big.py` now display meta v2 first (entity, decorators, header.signature, body.docstring/body.code) with legacy fallback.

## Notes
- Big batch may emit BrokenPipe when piping output; use without piping or adjust buffer.
- Visual start/end markers preserved for terminal listener.
