# ADR_20260501_atomic-file-writes-via-temp-directory

## Status

Accepted

## Context

smith must guarantee atomicity for the `connect` and `update` commands: either all agentic files are written to the project directory or none are. Partial connections are explicitly forbidden by the Safety and Atomicity quality attributes. The file set includes AGENTS.md (single file), .opencode/ (directory tree), .templates/ (directory tree), and .flowr/ (directory tree). The mechanism for achieving atomicity is architecturally significant because it affects the entire write path, rollback strategy, and failure recovery.

**Feature:** smith-commands (connect, update)

Forces:
- Atomicity quality attribute: "When smith connects, either all agentic files are written or none are" — Must priority
- Safety quality attribute: "When smith connects to a project that already has agentic files, it refuses to overwrite without explicit `--overwrite` flag" — Must priority
- Clean Separation quality attribute: "When smith disconnects, no agentic files remain" — Must priority
- Zero runtime dependency constraint — no external transaction managers
- The write set includes both single files and directory trees — the mechanism must handle both

## Interview

| Question | Answer |
|---|---|
| How should smith guarantee atomicity for file writes? | Temp-directory staging with atomic rename |

## Decision

Use temp-directory staging for all file writes: write all files to a temporary directory first, validate the complete set exists, then move files to their final locations. On any failure during the write phase, discard the temporary directory — no cleanup of partial writes needed because nothing was moved to the final location yet.

## Reason

Temp-directory staging is the simplest mechanism that satisfies the atomicity invariant without runtime dependencies. It uses only `tempfile.mkdtemp()` and `os.replace()` from the stdlib. The two-phase approach (stage → commit) means that failures during staging leave zero trace in the project directory, eliminating the need for complex rollback logic.

## Alternatives Considered

- **Transaction log with rollback**: Write a log of all operations before executing them; on failure, reverse the log. Rejected because it requires tracking individual file operations, makes rollback complex (reverse order, handle partial failures during rollback), and risks leaving the project in an inconsistent state if rollback itself fails.
- **Shadow directory (write to `.smith-staging/`, then rename)**: Similar to temp-directory staging but uses a fixed directory name in the project root. Rejected because it pollutes the project directory with a staging directory that must be cleaned up even on success, and could conflict with an existing `.smith-staging/` directory.
- **In-place writes with backup-and-restore**: Write files directly, keeping backups of any overwritten files. On failure, restore from backups. Rejected because it's the most complex approach — requires backup management, handles partial writes, and risks data loss if the restore fails.

## Consequences

- (+) Atomicity guarantee: either all files are written or none are — no partial connections possible
- (+) Simple rollback: on failure, just discard the temp directory — no cleanup of partial writes
- (+) Zero runtime dependencies — uses only stdlib (`tempfile`, `os.replace`, `shutil.move`)
- (+) Clear failure mode: if staging fails, the project directory is untouched
- (-) Disk space: staging requires temporary disk space for the full file set — mitigated by the fact that agentic files are typically small (a few KB for AGENTS.md, a few MB for .opencode/)
- (-) Two-phase write adds latency: all files must be staged before any are committed — mitigated by the small file set size
- (-) `os.replace()` is atomic on POSIX but not on Windows for cross-device moves — mitigated by ensuring temp directory is on the same filesystem as the project directory (use `dir=` parameter of `mkdtemp`)

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Accepted? |
|------|------------|--------|------------|-----------|
| Cross-device temp directory causes non-atomic rename on Windows | Low | Medium | Use `dir=` parameter of `mkdtemp` to create temp directory in the project directory's filesystem | Yes |
| Staging directory leaked if process is killed between stage and commit | Low | Low | Add a `.smith-staging` cleanup check at the start of `smith connect` and `smith status` | Yes |
| Disk full during staging causes write failure | Low | Low | Pre-check available disk space before staging; report clear error message | Yes |
| File permissions differ between temp and project directories | Low | Low | Explicitly set permissions after `os.replace()` using `os.chmod()` | Yes |