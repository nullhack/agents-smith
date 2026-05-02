# ADR_20260502_overwrite-protection

## Status

Accepted

## Context

When clone runs on a project that already has some smith-managed files (e.g., from a previous clone or manual setup), it needs to decide whether to overwrite existing content. Overwriting without consent could destroy customizations; never overwriting prevents intentional updates.

## Interview

| Question | Answer |
|---|---|
| Should existing files be overwritten by default? | No — safety first |
| Should existing directories be treated differently from files? | No — if a directory exists, skip it entirely (don't merge) |

## Decision

By default, clone skips any file or directory that already exists. The --overwrite flag opts in to overwriting. Directory-level skipping means if .opencode/ exists, none of the new .opencode/ files are written.

## Reason

Safety-first default prevents accidental data loss. Directory-level skipping (rather than file-level merging) is simpler to reason about and prevents partial updates that could leave a directory in an inconsistent state.

## Alternatives Considered

- **File-level merging within directories**: More granular but complex; risks merging old and new configs in ways that break
- **Prompt for each file**: Interactive prompts don't work in scripted/CI environments

## Consequences

- (+) Safe default — no data loss without explicit --overwrite
- (+) Simple mental model — entire directories are either skipped or overwritten
- (-) Directory-level skipping means a single existing file in a directory blocks all new files in that directory

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Accepted? |
|------|------------|--------|------------|-----------|
| User expects partial merge within directories | Low | Low | Documentation clarifies directory-level behavior | Yes |