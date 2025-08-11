# Python Scope Detection — Testing Plan (2025-08-11)

## Objectives
- Validate correctness on realistic Python patterns before enabling recursive ancestry.
- Keep tests readable with small fixtures and targeted assertions.

## Test fixtures
- `fixtures/decorators.py`: decorated functions/classes; stacked decorators; async def
- `fixtures/nested.py`: class-within-class (if any), function within class, nested function
- `fixtures/control_flow.py`: if/elif/else with returns; try/except/finally
- `fixtures/docstrings.py`: single-line and triple-quoted docstrings; blank lines
- `fixtures/multiline_sigs.py`: function signatures across multiple lines
- `fixtures/edge_spacing.py`: consecutive scopes without blank lines; tabs vs spaces

## Test cases
- For each fixture, pick starts at headers and mid-scope lines; assert [start, end] ranges and validity flags.
- Ensure class/function boundaries exclude the next header line, include docstrings/comments inside.
- Validate decorator inclusion: start shifts upward to include contiguous `@...` lines above the `def`.
- Negative cases: invalid indent patterns marked invalid; min scan enforcement.

## Ancestry tests (phase 2)
- For a given line, assert the sequence of ancestor scopes (innermost → outermost) with correct types and ranges.
- Cross-check with manually computed stack from the fixture.

## Tooling
- Extend the debug runner with an option to print ancestry chain.
- Keep timeout short; use only local parsing.
