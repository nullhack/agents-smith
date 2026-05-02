Feature: Gitignore Section Management

  The system manages a delimited section in the project's .gitignore file to track which files and directories smith has installed. This section uses start and end markers so it can be created, replaced, or read idempotently.

  Status: BASELINED (2026-05-02)

  Rules (Business):
  - The smith-managed section is delimited by "# smith managed" (start) and "# end smith managed" (end) markers
  - When a section already exists, add_section replaces it in-place rather than appending a duplicate
  - get_patterns returns only non-blank, non-comment lines between the markers
  - If no .gitignore file exists, add_section creates one
  - The .gitignore file always ends with a newline

  Constraints:
  - The gitignore section must never modify content outside the markers
  - The section must remain idempotent — running add_section twice with the same patterns produces the same result

  ## Frozen Examples Rule

  After a feature is BASELINED, all `Example:` blocks are immutable. Changes require
  `@deprecated` on the old Example (preserving the original @id) and a new Example
  with a new @id.

  `@id` tags are for traceability only — do NOT add priority tags to Examples.

  ## Questions

  | ID | Question | Status | Answer / Assumption |
  |----|----------|--------|---------------------|
  | Q1 | Should the section be placed at the end of .gitignore or at the beginning? | Resolved | At the end — appended if no existing section |
  | Q2 | Should a trailing newline be ensured after the end marker? | Resolved | Yes — the file always ends with a newline |

  ## Changes

  | Session | Q-IDs | Change |
  |---------|-------|--------|
  | 2026-05-02 | Q1, Q2 | Created: gitignore management feature derived from test suite |

  Rule: Creating a managed section
    As a developer
    I want smith to add a managed section to .gitignore listing installed files
    So that git ignores smith-managed files and purge knows what to remove

  @id:gitignore-create-section
    Example: Creates .gitignore with managed section when none exists
      Given a project directory with no .gitignore file
      When smith adds a section with patterns ["AGENTS.md", ".opencode/"]
      Then .gitignore contains "# smith managed" followed by "AGENTS.md" and ".opencode/" and "# end smith managed"

  @id:gitignore-append-to-existing
    Example: Appends managed section to existing .gitignore
      Given a project directory with .gitignore containing "node_modules/" and "dist/"
      When smith adds a section with patterns ["AGENTS.md"]
      Then .gitignore preserves "node_modules/" and "dist/" and appends the managed section

  @id:gitignore-replace-existing-section
    Example: Replaces existing managed section in-place
      Given a project directory with .gitignore containing a managed section listing "AGENTS.md"
      When smith adds a section with patterns [".opencode/", ".flowr/"]
      Then .gitignore preserves content outside the section and replaces the section content with ".opencode/" and ".flowr/", removing "AGENTS.md"

  Rule: Detecting a managed section
    As a developer
    I want smith to detect whether a managed section exists
    So that it knows whether purge can proceed

  @id:gitignore-has-section
    Example: Returns true when managed section exists
      Given a project directory with .gitignore containing "# smith managed\nAGENTS.md\n# end smith managed"
      When smith checks for the managed section
      Then it returns true

  @id:gitignore-no-section
    Example: Returns false when no managed section exists
      Given a project directory with .gitignore containing only "node_modules/"
      When smith checks for the managed section
      Then it returns false

  @id:gitignore-no-file
    Example: Returns false when no .gitignore exists
      Given a project directory with no .gitignore file
      When smith checks for the managed section
      Then it returns false

  Rule: Reading patterns from the managed section
    As a developer
    I want smith to read the patterns listed in the managed section
    So that purge knows which files and directories to remove

  @id:gitignore-get-patterns
    Example: Returns patterns from managed section
      Given a project directory with .gitignore containing "# smith managed\nAGENTS.md\n.opencode/\n# end smith managed"
      When smith reads the patterns
      Then it returns ["AGENTS.md", ".opencode/"]

  @id:gitignore-skip-comments-blanks
    Example: Skips comments and blank lines in the section
      Given a project directory with .gitignore containing "# smith managed\n# a comment\nAGENTS.md\n\n.opencode/\n# end smith managed"
      When smith reads the patterns
      Then it returns ["AGENTS.md", ".opencode/"]