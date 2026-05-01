# ADR_20260501_no-smart-merge

## Status

Accepted

## Context

When `smith connect` encounters an existing `.flowr/` or `.templates/` directory in the target project, a decision must be made about how to handle the conflict. These directories may contain project-specific data (flows, templates) that the engineer has customised. The stakeholder deferred this decision to the architect.

Forces:
- Safety quality attribute: "Zero silent overwrites, ever"
- Atomicity quality attribute: "No partial connections, ever"
- Clean Separation quality attribute: "Zero orphaned files after disconnect"
- `.flowr/` and `.templates/` may contain project-specific data that the engineer wants to preserve
- Smart merge logic (comparing files, choosing which to keep) adds complexity and failure modes
- smith disconnect must be able to cleanly remove everything smith wrote — merge makes this ambiguous

## Interview

| Question | Answer |
|---|---|
| How should smith handle existing .flowr/ and .templates/ when connecting? | Refuse without --overwrite; replace entirely with --overwrite (no merge) |

## Decision

Treat `.flowr/` and `.templates/` identically to all other agentic files: skip user-tracked files and auto-update smith-managed files. When `--overwrite` is passed, replace managed files entirely. No smart merge logic.

## Reason

This decision applies the YAGNI principle over DRY. Smart merge logic would violate Atomicity (partial connections where some files are merged and others are skipped), Safety (silent modification of existing content), and Clean Separation (disconnect wouldn't know which files were smith's vs pre-existing). The simple mental model — "smith writes its files; if they exist, use `--overwrite`" — is more usable than complex merge rules.

## Alternatives Considered

- **Smart merge (file-by-file comparison):** Compare each file and only write files that don't exist. Rejected because it violates Atomicity (partial state: some files merged, some skipped), Safety (silently modifying existing directory content), and Clean Separation (disconnect can't determine which files were smith's).
- **Selective skip:** Skip `.flowr/` and `.templates/` if they exist, but write `AGENTS.md` and `.opencode/`. Rejected because it violates Atomicity (partial connection) and creates an inconsistent state where some agentic files are present but others are not.
- **Interactive prompt:** Ask the user what to do for each conflicting directory. Rejected because it breaks the non-interactive CLI workflow and adds complexity for a marginal benefit.

## Consequences

- (+) Atomicity is preserved: all files or nothing
- (+) Safety is preserved: no silent overwrites without `--overwrite`
- (+) Clean Separation is preserved: disconnect removes everything smith wrote, unambiguously
- (+) Simple mental model: "smith writes its files; if they exist, use `--overwrite`"
- (+) YAGNI: no merge logic to maintain, test, or debug
- (-) Engineers who want to combine project-specific flows/templates with smith's templates must manually manage that outside of smith — mitigated by the fact that `smith update --overwrite` replaces all files, making the workflow explicit

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Accepted? |
|------|------------|--------|------------|-----------|
| Engineers lose project-specific .flowr/ or .templates/ data when using --overwrite | Medium | High | Warn before overwrite; suggest backing up the directory first. Future feature could add `--backup` flag | Yes |
| Engineers want selective merge in future | Low | Low | Can be added as a future feature without architectural changes — the TemplateSourcePort and FileSystemPort interfaces support this | Yes |