# Interview Notes: smith-commands Feature Specification

> **Date:** 2026-05-01
> **Feature:** smith-commands (connect, disconnect, update, status)
> **Interviewer:** PO
> **Stakeholder:** nullhack
> **Session type:** Feature specification (behavioral rules and edge cases)

---

## General Behavioral Rules

### Stateless Operation

- **smith is stateless.** There is no `.smith.yaml` metadata file. No connection state is stored.
- Connection state is inferred from the presence of the `# smith managed` section in `.gitignore` and which agentic files exist on disk.
- `smith connect`, `smith update`, and `smith disconnect` are stateless operations — they write or remove files based on what's currently on disk.

### Agentic Files

- The agentic file set is: **AGENTS.md**, **.opencode/**, **.templates/**, **.flowr/**
- **Pair-atomic rule:** AGENTS.md and .opencode/ are a pair — either both are written or neither. This is the core atomicity invariant.
- **.templates/ and .flowr/ are independent:** if they don't exist, they are written; if they already exist (and are gitignored by the `# smith managed` section), they are refused unless `--overwrite` is used.

### .gitignore Section

- On connect, smith adds a `# smith managed` section to `.gitignore` with entries for each agentic file pattern.
- On disconnect, smith **keeps** the `# smith managed` section in `.gitignore`. It serves as a guard for future smith usage — it records which files are agentic and should be treated specially.
- Disconnect removes the agentic files that are gitignored (i.e., listed in the `# smith managed` section). If a file/folder is in the agentic set but the `.gitignore` section does NOT ignore it, that means the user explicitly wants to track it — so smith does NOT remove it.
- If a `.gitignore` entry for an agentic file/folder is NOT preceded by `# smith managed` (i.e., the user added it manually outside the section), smith does not modify that entry.

### Template Source

- Default template source: **agents-smith** (bundled with the agents-smith package).
- Override with `--from <source>`:
  - Local path: `--from ./my-templates`
  - URL: `--from https://example.com/templates.tar.gz`
  - Git repo: `--from git+https://github.com/user/repo.git#branch` (standard URL format with ref parameter)
- If `--from` points to a non-existent path or unreachable URL: **error, exit 1**.

---

## Command Behavioral Rules

### `smith connect [--from <source>] [--overwrite]`

**Default behavior (fresh project, no agentic files):**
1. Resolve template source (default: agents-smith, or `--from`).
2. Stage all agentic files in a temp directory.
3. Validate: check for conflicts (existing agentic files).
4. Write AGENTS.md + .opencode/ atomically (pair-atomic: both or neither).
5. Write .templates/ independently (if absent, write it; if present and not gitignored by smith, refuse).
6. Write .flowr/ independently (same rule as .templates/).
7. Add `# smith managed` section to `.gitignore` with entries for all agentic files.
8. Report success: list files written.

**When agentic files already exist:**
- If any agentic file/folder exists and IS gitignored by the `# smith managed` section → **conflict, exit 2**, list conflicting files, suggest `--overwrite`.
- If an agentic file/folder exists but is NOT in the `# smith managed` section (user tracks it manually) → do not overwrite it, skip it, write the rest. The user explicitly chose to track this file.
- `--overwrite`: replace ALL agentic files that are in the `# smith managed` section, regardless of conflicts. Does NOT touch files not in the smith-managed section.

**When already connected (`.gitignore` has `# smith managed` section):**
- `smith connect` on an already-connected project = **auto-update** (same behavior as `smith update`).
- `smith connect --from <new_source>` on an already-connected project = update from the new source.

**Exit codes:** 0 = success, 1 = error (invalid args, source not found, IO failure), 2 = conflict (files exist without `--overwrite`).

### `smith disconnect`

**Default behavior (connected project):**
1. Identify agentic files listed in the `# smith managed` section of `.gitignore`.
2. Remove only the agentic files that ARE gitignored by the `# smith managed` section.
3. If an agentic file/folder is NOT gitignored by `# smith managed` (user chose to track it), do NOT remove it.
4. Keep the `# smith managed` section in `.gitignore` (it serves as a guard for future usage).
5. Report success: list files removed.

**When not connected (no `# smith managed` section):**
- **No-op, exit 0.** No error, no message needed.

**When partially connected (some agentic files missing):**
- Remove whatever agentic files ARE present and gitignored by `# smith managed`. No error for missing files.

**Exit codes:** 0 = success (including no-op), 1 = error (IO failure).

### `smith update [--from <source>]`

**Default behavior (connected project):**
1. Resolve template source (default: agents-smith, or `--from`).
2. Re-download all agentic files from the template source.
3. Overwrite ALL agentic files that are in the `# smith managed` section (this is an intentional overwrite — update is the "refresh" operation).
4. Do NOT touch files not managed by smith.
5. Maintain the pair-atomic rule for AGENTS.md + .opencode/ (both or neither).
6. Report success: list files updated.

**When not connected (no `# smith managed` section in `.gitignore`):**
- **Auto-connect:** same behavior as `smith connect` with the same `--from` flag.

**When `--from` source is not found:**
- **Error, exit 1.**

**Exit codes:** 0 = success, 1 = error (source not found, IO failure).

### `smith status [--json]`

**Default behavior (human-readable):**
- Check which agentic files exist on disk.
- If all agentic files present → report "Connected" with file list and template source (if determinable).
- If some agentic files present → report "Partial" with which files are present/missing, suggest `smith connect --overwrite` or `smith disconnect`.
- If no agentic files present but `# smith managed` section exists in `.gitignore` → report "Disconnected" with suggestion to `smith connect` to reconnect.
- If no agentic files and no `# smith managed` section → report "Not connected" with "Run smith connect to get started."

**With `--json` flag:**
- Machine-readable JSON output with same information, suitable for scripting.

**Exit codes:** 0 = success, 1 = error.

---

## Edge Cases and Failure Modes

### Partial connection (some files written, then failure)

- The pair-atomic rule for AGENTS.md + .opencode/ means: if writing .opencode/ fails, AGENTS.md must be rolled back too. Both succeed or neither.
- .templates/ and .flowr/ are independent — a failure writing .flowr/ does not roll back .templates/.
- Temp-directory staging is used for AGENTS.md + .opencode/ to ensure atomicity.

### .gitignore section manipulation

- If `.gitignore` doesn't exist, create it with the `# smith managed` section.
- If `.gitignore` exists but doesn't have a `# smith managed` section, append the section at the end.
- If `.gitignore` has a `# smith managed` section already, update entries within it (add missing entries, do not remove existing entries unless they are for smith-managed files being disconnected).

### User-modified agentic files

- `smith disconnect` removes agentic files that are gitignored by `# smith managed`, regardless of whether the user modified them. This is clean separation.
- If the user wants to keep their changes, they should NOT gitignore the file (remove it from the `# smith managed` section), and smith will not remove it on disconnect.

### Template source failure mid-write

- If the template source fails during download/extraction, exit 1 with an error message. No partial writes for the atomic pair (AGENTS.md + .opencode/).

---

## Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| State management | Stateless — no .smith.yaml | Simpler model; .gitignore section is sufficient to track managed files |
| Atomicity scope | AGENTS.md + .opencode/ are pair-atomic; .templates/ and .flowr/ are independent | Core agent config must be consistent; template/flow dirs are independent concerns |
| .gitignore on disconnect | Keep `# smith managed` section | Serves as guard for future smith usage |
| File removal on disconnect | Remove only gitignored agentic files | Files the user explicitly tracks are preserved |
| Connect on already-connected | Auto-update (same as update) | No need to force disconnect first |
| Update on not-connected | Auto-connect | Convenient; same as connect |
| Disconnect on not-connected | No-op, exit 0 | Idempotent; no error for clean state |
| Template source types | Bundled (agents-smith), local path, URL, git repo | Full flexibility from the start |
| Git source format | `git+https://...#branch` | Standard URL format with ref parameter |
| Status output | Human-readable by default, `--json` for scripting | Dual audience |
| Exit codes | 0/1/2 — success/error/conflict | Simple, covers the main cases; conflict maps to safety invariant |