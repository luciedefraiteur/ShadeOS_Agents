# Python Scope Detection — Progress and Roadmap (2025-08-11)

## Current status
- Start alignment: when `start_line` is before a real scope header, shift to the first matching `def`/`class`.
- End detection: indentation-based for Python. A scope ends when indentation returns to the start indent (or less) on a non-empty line; the end line is the last non-blank line inside the scope body.
- Mid-scope safety: minimum scan window when starting mid-scope; strict invalidation when scanning too few lines.
- FIFO UX: debug runner prints index, absolute file path with ranges, explicit “scope trouvé” line, and scope content between markers with truncation.
- Duplicate listener purge: auto-kills duplicate listeners bound to the same FIFO to prevent command loss.

Validated example (`Core/Agents/V10/tests/debug_scope_source.py`):
- class `Greeter`: 5..12
- `greet`: 9..12
- `add`: 15..17
- `factorial`: 20..24

## Next improvements
1) Decorator inclusion
- Include one or more `@decorator` lines immediately above `def` in the detected scope start.
- Keep generic logic (do not depend on specific decorator names); detect lines `^\s*@\w.*` contiguous with the header.

2) Complex Python test suite (non-exhaustive)
- Nested class → nested function
- Function with `if/elif/else` and multiple returns
- Function with docstring (single/multiline) and blank lines
- Consecutive functions/classes without blank lines
- Decorated async functions
- Indentation anomalies (tabs vs spaces) — detect and mark invalid rather than guess
- Multiline signatures and default args spanning lines

3) Recursive scope ancestry discovery
- Given a file and a line, return the chain of enclosing scopes (innermost → outermost), including intermediate class/function scopes up to the module-level pseudo-scope.
- Use a single pass over the file to generate a stack of scopes by indentation transitions, recording [start, end] for each.
- A query at line L returns all scopes whose [start, end] contain L, sorted by depth.

4) Productionizing
- Provide a stable public API: `read_scope_at(file, line) -> {range, type, header, ancestors[]}`.
- Add runner flags to toggle “recursive ancestry” output.
- Robust error reporting and debug traces (indent stack transitions, header matches).

## Milestones
- M1: Decorator inclusion + add tests for decorated functions/classes
- M2: Complex test matrix green (nested, control flow, docstrings, multiline)
- M3: Recursive ancestry API and runner output
- M4: Integration into specialized tool with feature flag, docs and examples
