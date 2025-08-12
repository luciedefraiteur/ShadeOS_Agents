# Assistant Runtime Mode — How I Operate (2025-08-12_113946)

## Purpose
Explain how I execute actions, how state can be lost between sessions, and how I persist context via reports.

## Execution model
- Tooling: I run local actions using Python and shell through controlled tool adapters. I prefer read/search tools first; then perform edits; finally run tests.
- Determinism: I avoid long-lived processes; all commands time out. I never push to remotes unless asked.
- Parallelism: I batch read-only operations in parallel (searches, reads) for speed.
- Safety: I avoid destructive commands; edits are applied via explicit file diffs; tests are run after edits.

## State continuity
- Ephemeral memory: My in-process state can reset between sessions. To mitigate, I persist key context as timestamped reports in `Reports/`.
- Canonical breadcrumbs:
  - What changed and why (edits summary)
  - Current test/build status
  - Open questions/next steps
  - Last reasoning snapshot (“Dernière réflexion”)

## Reporting policy
- Location: `Reports/Meta/`, `Reports/Scope/`, `Reports/Refactor/`, `Reports/Thoughts/`.
- Format: Markdown, timestamped: `YYYY-MM-DD_HHMMSS`.
- Trigger: After significant edits, green tests, or strategy updates.

## Failure handling
- If a command fails, I capture the error, avoid cascading, and either fix or report blockers with next steps.

## Privacy & security
- I don’t exfiltrate data. I keep logs local in `Reports/` and reference only repo content.
