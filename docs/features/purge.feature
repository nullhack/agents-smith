Feature: Purge

  The purge command reads the smith-managed section in .gitignore and deletes every file and directory listed there. It does not remove the .gitignore section itself, allowing reclone to update it. If no managed section exists, purge is a no-op.

  Status: BASELINED (2026-05-02)

  Rules (Business):
  - Purge only removes files and directories listed in the smith-managed .gitignore section
  - Files and directories NOT listed in the managed section are never touched
  - The .gitignore file itself and its managed section are preserved after purge
  - If no managed section exists, purge returns an empty list and takes no action

  Constraints:
  - Purge must never delete files that are not tracked in the managed section
  - Purge must be safe to run on a project that was never cloned

  ## Frozen Examples Rule

  After a feature is BASELINED, all `Example:` blocks are immutable. Changes require
  `@deprecated` on the old Example (preserving the original @id) and a new Example
  with a new @id.

  `@id` tags are for traceability only — do NOT add priority tags to Examples.

  ## Questions

  | ID | Question | Status | Answer / Assumption |
  |----|----------|--------|---------------------|
  | Q1 | Should purge remove the .gitignore section markers? | Resolved | No — the section is preserved so reclone can update it |

  ## Changes

  | Session | Q-IDs | Change |
  |---------|-------|--------|
  | 2026-05-02 | Q1 | Created: purge feature derived from test suite |

  Rule: Removing tracked files
    As a developer
    I want purge to remove all files and directories tracked in the managed section
    So that I can cleanly remove smith-managed configuration from my project

  @id:purge-removes-tracked
    Example: Removes files and directories listed in managed section
      Given a project with AGENTS.md, .opencode/ directory, and .gitignore containing "# smith managed\nAGENTS.md\n.opencode/\n# end smith managed"
      When the developer runs purge
      Then AGENTS.md is deleted
      And .opencode/ directory is deleted
      And the managed section in .gitignore is preserved

  @id:purge-preserves-untracked
    Example: Only deletes files listed in managed section
      Given a project with AGENTS.md, README.md, and .gitignore containing "# smith managed\nAGENTS.md\n# end smith managed"
      When the developer runs purge
      Then AGENTS.md is deleted
      And README.md is preserved

  Rule: No managed section
    As a developer
    I want purge to be a no-op when no managed section exists
    So that running purge on a project that was never cloned is safe

  @id:purge-no-section-noop
    Example: Returns empty list when no managed section exists
      Given a project with AGENTS.md but no smith-managed section in .gitignore
      When the developer runs purge
      Then no files are deleted
      And AGENTS.md is preserved