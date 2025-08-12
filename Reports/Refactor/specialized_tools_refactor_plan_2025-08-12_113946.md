# Refactor Plan — V10 Specialized Tools (2025-08-12_113946)

## Motivation
`Core/Agents/V10/specialized_tools.py` is too large; split responsibilities to improve clarity and testability.

## Target structure
- tools/io_lines.py — read/write/replace lines tools
- tools/analysis.py — analyze structure, create index, summarize chunk/section
- tools/scope_detection/python_scope.py — Python scope detector and helpers
- tools/scope_detection/reader.py — ReadChunksUntilScope tool
- tools/registry.py — V10SpecializedToolsRegistry (public API)

## Migration steps
1) Extract classes keeping imports stable and no behavior change.
2) Keep `specialized_tools.py` re-exporting registry for backward compatibility.
3) Run scope tests, then full V10 tests incrementally.
4) Follow-up: isolate AST metadata helpers; add ancestry API.

## Risks
- Import paths breakage — mitigate with re-exports and staged commits.
- Hidden coupling — address with thin adapters.
