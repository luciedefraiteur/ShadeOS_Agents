# Vibe Coding Dev Agent — How To Proceed (Live Scope Detection)

## Where to start
- Read: Reports/Scope/python_ast_integration_plan_YYYY-MM-DD_HHMMSS.md (AST validation plan)
- Read: Reports/Scope/python_vibe_coding_integration_plan_YYYY-MM-DD_HHMMSS.md (Vibe Coding plan)

## Local validation (before FIFO)
1) Run the heavy mid-scope suite locally:
   ```bash
   PYTHONPATH=$REPO_ROOT python -m pytest -q Core/Agents/V10/tests/test_scope_mid_scope_heavy.py
   ```
2) Inspect boundaries with the debug runner:
   ```bash
   PYTHONPATH=$REPO_ROOT:$PYTHONPATH python Core/Agents/V10/tests/debug_scope_runner.py
   ```
   - Expect output with [index], absolute file:line ranges, "scope trouvé" line, and **SCOPE_START/END** markers.
3) Check integrity flags in scope_boundaries.issues:
   - unterminated_scope_eof, unterminated_string, unbalanced_delimiters_scope (as applicable)
4) Never wrap snippets for parsing; AST is only for notes (ast_notes).

## FIFO validation (only after local green)
- Ensure single listener on FIFO (/tmp/shadeos_cmd.fifo). Foreground recommended:
  ```bash
  TTY=$(readlink /proc/$$/fd/1)
  python shadeos_term_listener.py --fifo /tmp/shadeos_cmd.fifo \
    --cwd $REPO_ROOT --tty "$TTY" --echo --log /tmp/shadeos_listener.log --print-ready
  ```
- Send the debug runner via injector:
  ```bash
  python shadeos_term_exec.py --cmd "cd $REPO_ROOT && PYTHONPATH=$REPO_ROOT:$PYTHONPATH python Core/Agents/V10/tests/debug_scope_runner.py"
  ```

## Current progress checklist
- [x] Python heuristic: header recenter (def/class + decorators), indent-based end
- [x] AST validation: no wrapping, notes only (ast_invalid_snippet)
- [ ] EOF unterminated flag reliable in all cases
- [ ] Decorated method end includes final return
- [ ] Ancestry discovery (enclosing scopes up to module)

## TFME integration (next)
- Create temporal nodes per scope with:
  - content (truncated if needed), file_path, start_line, end_line, indent_level, issues[], summary
- Link nodes: contains/contained_in (once ancestry implemented), prev/next
- Dev Agent prioritizes nodes with issues for quick fixes
