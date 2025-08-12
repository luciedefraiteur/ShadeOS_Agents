# Scope Detector — Progress Snapshot (2025-08-12_121644)

## What’s done
- Decorator-aware start alignment (tolerates interleaved comments/blank lines).
- Multi-line header signature detection; `meta.header_signature` exposed.
- Docstring split-out and `meta.body_executable` exposed.
- Debug runners: small batch + big batch with visual markers and anchors.

## Tests
- Scope tool, mid-scope heavy, advanced: all green locally.
- Big fixture batch (18 queries): ALL GREEN.

## Next
- Ancestry chain output in runners.
- Refactor specialized tools into modules (no API break).
