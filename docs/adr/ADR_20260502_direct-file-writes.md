# ADR_20260502_direct-file-writes

## Status

Accepted

## Context

When smith clones a project, it writes multiple files and updates .gitignore. If a write fails partway through, the project could be left in a partial state — some files written, some not. The main branch uses atomic writes via temp-directory staging, but the current rebuild (minimal-v2) intentionally reduces scope.

## Interview

| Question | Answer |
|---|---|
| Is partial-state prevention a requirement? | Nice to have, but not at the cost of complexity for two commands |
| What is the failure mode? | Rare — filesystem writes almost never fail; network fetch failures happen before any writes |

## Decision

Write files directly to the project directory without temp-directory staging. If a write fails partway through, some files may exist and others may not. The user can re-run clone to complete the operation.

## Reason

Atomic writes add significant implementation complexity (temp directory management, staging, atomic rename, rollback). For the current scope (two commands, no concurrent access, rare failure mode), direct writes are simpler and sufficient. The failure mode (partial state) is recoverable by re-running clone. If atomicity becomes a hard requirement, a staging layer can be added without changing the core API.

## Alternatives Considered

- **Atomic writes via temp-directory staging**: Main branch uses this pattern. Writes all files to a temp directory first, then moves them atomically. On failure, discards the temp directory. Adds significant complexity for a rare failure mode.
- **Transaction log**: Record intent before writing, clean up on next run. Even more complex than temp-directory staging.

## Consequences

- (+) Simple implementation — no temp directory management, no rollback logic
- (+) Fast — no double-write overhead
- (-) Partial state is possible if a write fails mid-operation
- (-) Re-running clone is the recovery mechanism (no automatic rollback)

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Accepted? |
|------|------------|--------|------------|-----------|
| Partial state from mid-operation failure | Low | Medium | Re-run clone to complete; purge to clean up | Yes |
| User confusion about partial state | Low | Low | Error messages guide user to re-run clone | Yes |