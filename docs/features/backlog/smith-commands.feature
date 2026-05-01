Feature: smith-commands

  smith connects standardised agent configurations (AGENTS.md, .opencode/,
  .templates/, .flowr/) to any project directory and disconnects cleanly when
  done. Four commands — connect, disconnect, update, status — validate the
  full connect/work/disconnect cycle end-to-end.

  Status: BASELINED (2026-05-01)

  Rules (Business):
  - Connection state is inferred from the `# smith managed` section in .gitignore, not from a metadata file
  - All agentic files are written atomically: either all are written or none are
  - .templates/ and .flowr/ follow the same atomic rules as AGENTS.md and .opencode/
  - Existing files gitignored by `# smith managed` are auto-updated; files NOT in that section are skipped
  - Disconnect removes only gitignored managed files; user-tracked files are preserved
  - `# smith managed` section is kept on disconnect (guard for future usage)
  - Connect on already-connected project auto-updates; update on not-connected project auto-connects

  Constraints:
  - Safety: zero silent overwrites, ever (product_definition.md #1)
  - Atomicity: no partial connections, ever (product_definition.md #2)
  - Clean separation: zero orphaned files after disconnect (product_definition.md #3)
  - Usability: smith connect must complete in under 1 minute (product_definition.md #4)

  ## Frozen Examples Rule

  After a feature is BASELINED, all `Example:` blocks are immutable. Changes require
  `@deprecated` on the old Example (preserving the original @id) and a new Example
  with a new @id. This prevents scope creep and maintains traceability.

  ## Pre-Mortem Findings

  | Rule | Failure Mode | Mitigation Example |
  |------|-------------|-------------------|
  | 1 — Connect | .gitignore does not exist → smith cannot add managed section | c928a845: creates .gitignore |
  | 1 — Connect | .gitignore exists without smith section → append fails silently | 86c8e268: appends section to existing file |
  | 2 — Skip | User adds .gitignore entries outside `# smith managed` for smith files → smith treats them as user-tracked | df0455a5: smith-managed file is auto-updated on reconnect |
  | 3 — Disconnect | User manually deleted a managed file before disconnect | b755bfae: partial disconnect is idempotent |
  | 4 — Update | Template source has changed since last connect (files added/removed) | 9a01f4e2: update reflects current template state |

  ## Questions

  | ID | Question | Status | Answer / Assumption |
  |----|----------|--------|---------------------|
  | Q1 | Should `smith status --json` include the template source URL in the output? | Assumed | Yes — status should report whatever connection metadata is available |
  | Q2 | What happens if .gitignore is read-only? | Assumed | Exit 1 with IO error (standard filesystem error, not a smith-specific exit code) |
  | Q3 | What happens if a managed file is a broken symlink? | Assumed | Treat as present (it exists on disk as a symlink); smith does not resolve symlinks |
| Q4 | What happens if the bundled template download fails on first connect? | Assumed | N/A — bundled source reads from local package data, no network required |
  | Q5 | What happens if the bundled template download fails but cache exists? | Assumed | N/A — bundled source reads from local package data, no caching |

  ## Changes

  | Session | Q-IDs | Change |
  |---------|-------|--------|
  | 2026-05-01 SN | — | Created: initial BDD specification for smith-commands |
| 2026-05-01 SN | IN_20260501_agents-smith-dependency-resolution | Added: bundled template network failure and cache fallback examples (a1b2c3d4, e5f6g7h8); added Q4 and Q5 about network failure behavior |
| 2026-05-01 SN | IN_20260501_local-bundle-reversal | Deprecated: a1b2c3d4 and e5f6g7h8 (bundled source no longer uses network); Added: URL source download failure examples (a2b3c4d5, e4f5g6h7); Updated Q4/Q5 to reflect local bundle |

  Rule: Connect to a fresh project
    As an engineer
    I want to run smith connect in a fresh project directory
    So that I can immediately start using standard AI agent workflows

    @id:c928a845
    Example: Connect with default template source
      Given a project directory with no agentic files and no `# smith managed` section in .gitignore
      When the engineer runs `smith connect`
      Then all agentic files (AGENTS.md, .opencode/, .templates/, .flowr/) are written to the project directory
      And a `# smith managed` section is added to .gitignore with entries for all agentic file patterns

    @id:86c8e268
    Example: Connect with a local path template source
      Given a project directory with no agentic files
      When the engineer runs `smith connect --from ./my-templates`
      Then agentic files are written from the local path template source to the project directory
      And a `# smith managed` section is added to .gitignore

    @id:577156bb
    Example: Connect with a URL template source
      Given a project directory with no agentic files
      When the engineer runs `smith connect --from https://example.com/templates.tar.gz`
      Then agentic files are downloaded from the URL and written to the project directory
      And a `# smith managed` section is added to .gitignore

    @id:4fdd38a4
    Example: Connect with a remote URL template source
      Given a project directory with no agentic files
      When the engineer runs `smith connect --from https://example.com/templates/my-template.zip`
      Then agentic files are downloaded from the remote URL and written to the project directory
      And a `# smith managed` section is added to .gitignore

    @id:f79d40f4
    Example: Template source not found
      Given a project directory with no agentic files
      When the engineer runs `smith connect --from /nonexistent/path`
      Then smith exits with code 1
      And an error message indicates the template source could not be found

    @id:a1b2c3d4 @deprecated(reason="bundled source no longer uses network; see a2b3c4d5 for URL failure")
    Example: Bundled template source network failure
      Given a project directory with no agentic files and no cached templates
      When the engineer runs `smith connect` and the GitHub archive download fails
      Then smith exits with code 1
      And an error message indicates the bundled template source could not be downloaded

    @id:e5f6g7h8 @deprecated(reason="bundled source no longer caches; see e4f5g6h7 for URL failure")
    Example: Bundled template source uses cache when network unavailable
      Given a project directory with no agentic files and cached templates from a previous connect
      When the engineer runs `smith connect` and the GitHub archive download fails
      Then smith uses the cached templates and connects successfully
      And smith exits with code 0

    @id:a2b3c4d5 Should
    Example: URL template source download failure
      Given a project directory with no agentic files
      When the engineer runs `smith connect --from https://example.com/templates.tar.gz` and the download fails
      Then smith exits with code 1
      And an error message indicates the URL template source could not be downloaded

    @id:e4f5g6h7 Should
    Example: URL template source invalid archive
      Given a project directory with no agentic files
      When the engineer runs `smith connect --from https://example.com/templates.tar.gz` and the downloaded archive is invalid
      Then smith exits with code 1
      And an error message indicates the archive could not be extracted

    @id:060390bf
    Example: Connect creates .gitignore when it does not exist
      Given a project directory with no agentic files and no .gitignore file
      When the engineer runs `smith connect`
      Then a new .gitignore file is created containing the `# smith managed` section with entries for all agentic file patterns

    @id:e8245392
    Example: Connect appends section to existing .gitignore
      Given a project directory with no agentic files and an existing .gitignore without a `# smith managed` section
      When the engineer runs `smith connect`
      Then the `# smith managed` section is appended to the existing .gitignore
      And existing .gitignore content is preserved

    @id:fc22c286
    Example: Pair-atomic write rollback on failure
      Given a project directory with no agentic files
      When smith fails to write .opencode/ after writing AGENTS.md
      Then AGENTS.md is removed (rolled back)
      And no agentic files remain in the project directory

   Rule: Auto-update on connected projects, skip user-tracked files on fresh projects
     As an engineer
     I want smith to auto-update managed files when the project is already connected
     And to skip user-tracked files when connecting to a fresh project
     So that my existing work is never silently overwritten

     @id:df0455a5 Must
     Example: Existing smith-managed file is auto-updated on reconnect
       Given a project directory where .opencode/ exists and is listed in the `# smith managed` section of .gitignore
       When the engineer runs `smith connect`
       Then .opencode/ is updated with the template version (auto-update)
       And all other agentic files are written
       And smith exits with code 0

    @id:21c05bbb Must
    Example: Existing user-tracked file is skipped
      Given a project directory where AGENTS.md exists but is NOT in the `# smith managed` section of .gitignore (the user tracks it manually)
      When the engineer runs `smith connect`
      Then AGENTS.md is not overwritten
      And the remaining agentic files (.opencode/, .templates/, .flowr/) are written
      And a `# smith managed` section is added to .gitignore

    @id:2a5f83d0 Must
    Example: Overwrite flag replaces all managed files
      Given a project directory where .opencode/ exists and is listed in the `# smith managed` section of .gitignore
      When the engineer runs `smith connect --overwrite`
      Then .opencode/ is replaced with the template version
      And all agentic files are written
      And files not in the `# smith managed` section are not touched

    @id:3e206149 Must
    Example: Connect on already-connected project auto-updates
      Given a project directory with all agentic files present and a `# smith managed` section in .gitignore
      When the engineer runs `smith connect`
      Then smith behaves as `smith update` — all managed agentic files are overwritten with the template versions
      And smith exits with code 0

    @id:7d22e1d6 Should
    Example: Overwrite with user-tracked files preserved
      Given a project directory where AGENTS.md is NOT in `# smith managed` (user-tracked) and .opencode/ IS in `# smith managed`
      When the engineer runs `smith connect --overwrite`
      Then .opencode/ is replaced with the template version
      And AGENTS.md is not touched (it is not in the smith-managed section)

  Rule: Disconnect from a project
    As an engineer
    I want to run smith disconnect so that all smith-managed files are removed from my project
    So that I can cleanly separate smith from my project without leaving orphaned files

    @id:cd5ba959 Must
    Example: Disconnect a fully connected project
      Given a project directory with all agentic files present and a `# smith managed` section in .gitignore
      When the engineer runs `smith disconnect`
      Then all agentic files that are gitignored by `# smith managed` are removed from the project directory
      And the `# smith managed` section is preserved in .gitignore
      And files not gitignored by `# smith managed` are not removed

    @id:9411ceb4 Must
    Example: Disconnect a not-connected project is a no-op
      Given a project directory with no agentic files and no `# smith managed` section in .gitignore
      When the engineer runs `smith disconnect`
      Then smith exits with code 0
      And no files are modified

    @id:b755bfae Should
    Example: Disconnect a partially connected project removes present gitignored files
      Given a project directory where .opencode/ exists and is gitignored by `# smith managed` but .flowr/ is missing
      When the engineer runs `smith disconnect`
      Then .opencode/ is removed
      And no error is raised for the missing .flowr/
      And the `# smith managed` section is preserved in .gitignore

    @id:8f2a9018 Must
    Example: User-tracked agentic file is preserved on disconnect
      Given a project directory where AGENTS.md is NOT gitignored by `# smith managed` (user tracks it) but .opencode/ IS gitignored by `# smith managed`
      When the engineer runs `smith disconnect`
      Then .opencode/ is removed
      And AGENTS.md is not removed (it is not in the smith-managed section)
      And the `# smith managed` section is preserved in .gitignore

  Rule: Update agentic files
    As an engineer
    I want to run smith update so that my connected project gets the latest template files
    So that I can stay current with template changes without reconnecting

    @id:e4d06612 Must
    Example: Update a connected project
      Given a project directory with all agentic files present and a `# smith managed` section in .gitignore
      When the engineer runs `smith update`
      Then all agentic files that are in the `# smith managed` section are overwritten with the latest template versions
      And files not managed by smith are not touched
      And smith exits with code 0

    @id:d348166e Should
    Example: Update with a new template source
      Given a project directory with all agentic files present and a `# smith managed` section in .gitignore
      When the engineer runs `smith update --from ./new-templates`
      Then all managed agentic files are overwritten with files from the new template source
      And smith exits with code 0

    @id:9a01f4e2 Must
    Example: Update on a not-connected project auto-connects
      Given a project directory with no agentic files and no `# smith managed` section in .gitignore
      When the engineer runs `smith update`
      Then smith behaves as `smith connect` — all agentic files are written and a `# smith managed` section is added to .gitignore
      And smith exits with code 0

    @id:7af2f4d1 Must
    Example: Update source not found
      Given a connected project directory
      When the engineer runs `smith update --from /nonexistent/path`
      Then smith exits with code 1
      And an error message indicates the template source could not be found

  Rule: Check connection status
    As an engineer
    I want to run smith status so that I know whether my project is connected and which agentic files are present
    So that I can take appropriate action

    @id:447e3cbf Must
    Example: Connected project status
      Given a project directory with all agentic files present and a `# smith managed` section in .gitignore
      When the engineer runs `smith status`
      Then smith reports "Connected" with a list of present agentic files

    @id:3f364b1d Must
    Example: Partially connected project status
      Given a project directory where .opencode/ and AGENTS.md exist but .templates/ and .flowr/ are missing
      When the engineer runs `smith status`
      Then smith reports "Partial" with a list of present and missing agentic files
      And suggests `smith connect --overwrite` or `smith disconnect`

    @id:76e27d0a Must
    Example: Disconnected project status
      Given a project directory with no agentic files but a `# smith managed` section in .gitignore
      When the engineer runs `smith status`
      Then smith reports "Disconnected"
      And suggests `smith connect` to reconnect

    @id:94ebcd86 Must
    Example: Not connected project status
      Given a project directory with no agentic files and no `# smith managed` section in .gitignore
      When the engineer runs `smith status`
      Then smith reports "Not connected"
      And suggests `smith connect` to get started

    @id:10843402 Should
    Example: Status with JSON output
      Given a connected project directory
      When the engineer runs `smith status --json`
      Then smith outputs machine-readable JSON with connection status, present files list, and template source