# Python AST Integration Plan for Scope Detection (2025-08-11_122056)

## Objectives
- Leverage `Core.Partitioner.ast_partitioners.PythonASTPartitioner` to validate and, optionally, refine scope detection results for Python.

## Phase 1 — Validation only (non-invasive)
- After heuristic boundaries `[start,end]` are computed:
  - Extract `snippet = lines[start-1:end]`.
  - Try `ast.parse(snippet)`.
    - If fails: wrap into a dummy function body: `def __wrap__():\n` + indent(snippet). Try parse again.
      - If wrapper parses: set `issues += ['partial_snippet_wrapped_ok']` and `scope_boundaries['ast_valid']=False`.
      - If still fails: set `issues += ['invalid_syntax_ast']` and `ast_valid=False`.
    - If parses: `ast_valid=True`.
- File-level preflight: optionally `ast.parse(full_text)` and expose `metadata['file_issues']` if fails.
- Do not alter `[start,end]` in this phase.

## Phase 2 — Refinement (optional, behind feature flag)
- Use `PythonASTPartitioner.parse_content(full_text, path)` to get the AST tree.
- Walk top-level and nested nodes to find the innermost node (`FunctionDef`/`AsyncFunctionDef`/`ClassDef`) covering `start_line` (or the query line when starting mid-scope).
- Replace `[start,end]` with node-exact ranges when available; fallback to heuristic if AST fails.
- Keep decorators and docstrings inclusion consistent with the AST node’s `lineno`, `end_lineno` (Python ≥3.8).

## Error reporting & telemetry
- Add `scope_boundaries['ast_valid']` (bool) and `scope_boundaries['issues']` entries: `'invalid_syntax_ast'`, `'partial_snippet_wrapped_ok'`.
- Add `metadata['file_issues']` and `metadata['ast_notes']` for file-level diagnostics.

## Runner options
- `--ast-validate`: print AST status for snippet and (optional) file.
- `--show-file-issues`: echo file-level issues.

## Risks
- Very large files: AST parse cost; limit to snippet + optional file preflight with timeout.
- Legacy Python features: ensure compatibility with current interpreter.

## Rollout
- Implement Phase 1 now (low risk), keep Phase 2 behind a feature flag.
