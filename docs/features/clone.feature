Feature: Clone

  The clone command fetches template files from a source and writes them into the project directory, adding a managed section to .gitignore to track what was written. It respects overwrite protection — existing files and directories are skipped by default.

  Status: BASELINED (2026-05-02)

  Rules (Business):
  - Only files matching ALLOWED_TOPICS (AGENTS.md, .opencode/, .flowr/, .templates/) are written
  - Existing files and directories are skipped unless --overwrite is passed
  - After writing files, clone adds a managed .gitignore section listing the top-level patterns of what was written
  - Archive entries with a single common top-level directory have that prefix stripped (e.g., temple8-main/AGENTS.md → AGENTS.md)

  Constraints:
  - Clone must never write files outside the allowed topic prefixes
  - Purge must be able to reverse a clone operation by reading the .gitignore section

  ## Frozen Examples Rule

  After a feature is BASELINED, all `Example:` blocks are immutable. Changes require
  `@deprecated` on the old Example (preserving the original @id) and a new Example
  with a new @id.

  `@id` tags are for traceability only — do NOT add priority tags to Examples.

  ## Questions

  | ID | Question | Status | Answer / Assumption |
  |----|----------|--------|----------------------|
  | Q1 | Should --overwrite replace individual files within existing directories, or skip the entire directory? | Resolved | Skip the entire directory — if .opencode/ exists, none of the new .opencode/ files are written |

  ## Changes

  | Session | Q-IDs | Change |
  |---------|-------|--------|
  | 2026-05-02 | Q1 | Created: clone feature derived from test suite |

  Rule: Writing files and tracking in .gitignore
    As a developer
    I want clone to write template files to my project and track them in .gitignore
    So that the files are available and can be cleanly removed later

  @id:clone-writes-and-tracks
    Example: Clone writes files and creates .gitignore section
      Given a template source containing AGENTS.md and .opencode/agents/default.md
      When the developer runs clone on a project directory
      Then AGENTS.md and .opencode/agents/default.md are written to the project
      And .gitignore contains a "# smith managed" section listing "AGENTS.md" and ".opencode/"

  Rule: Overwrite protection
    As a developer
    I want clone to skip existing files and directories by default
    So that my customizations are not accidentally overwritten

  @id:clone-skips-existing
    Example: Skips existing files without overwrite flag
      Given a project directory with AGENTS.md containing "old content"
      And a template source with AGENTS.md containing "new content"
      When the developer runs clone without --overwrite
      Then AGENTS.md retains "old content"

  @id:clone-skips-existing-directory
    Example: Skips existing directories without overwrite flag
      Given a project directory with .opencode/existing.md
      And a template source with .opencode/agents/default.md
      When the developer runs clone without --overwrite
      Then .opencode/existing.md is preserved
      And .opencode/agents/default.md is NOT written

  @id:clone-overwrites-with-flag
    Example: Overwrites existing files with --overwrite flag
      Given a project directory with AGENTS.md containing "old content"
      And a template source with AGENTS.md containing "new content"
      When the developer runs clone with --overwrite
      Then AGENTS.md contains "new content"