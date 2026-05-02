# ADR_20260502_gitignore-section-markers

## Status

Accepted

## Context

When smith writes files to a project, it needs to track which files it installed so that purge can remove them later. The tracking mechanism must be idempotent (re-running clone should not create duplicate entries) and must not interfere with existing .gitignore content.

## Interview

| Question | Answer |
|---|---|
| How should smith track which files it manages? | Use a delimited section in .gitignore with start/end markers |
| Should the section be replaced or appended on re-clone? | Replaced in-place — the section reflects the current set of managed files |

## Decision

Use start (`# smith managed`) and end (`# end smith managed`) markers in .gitignore to delimit a managed section that lists top-level patterns of installed files.

## Reason

Markers allow idempotent replacement of the section without parsing or modifying the rest of .gitignore. The section acts as a lightweight "manifest" that purge can read to know what to remove.

## Alternatives Considered

- **Separate manifest file (e.g., .smith-manifest.json)**: Would work but adds another file to track; .gitignore is already in the project and git-tracked
- **Tag each file with a comment**: Would make .gitignore noisy and hard to replace atomically

## Consequences

- (+) Simple, human-readable, and git-visible tracking mechanism
- (+) Idempotent — re-running clone replaces the section, not duplicates it
- (-) If a user manually edits inside the markers, their changes are lost on next clone
- (-) Patterns are top-level only — smith cannot track individual nested files

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Accepted? |
|------|------------|--------|------------|-----------|
| User edits inside markers are overwritten on reclone | Low | Low | Document that the section is managed by smith | Yes |