Feature: Fetch

  The fetch function downloads and extracts template files from a source. It supports three source types: GitHub repositories (via shorthand or URL), HTTP URLs to zip/tar.gz archives, and local directory paths. Only files matching allowed topic prefixes are returned.

  Status: BASELINED (2026-05-02)

  Rules (Business):
  - Source strings starting with "github:" are resolved to GitHub archive downloads
  - URLs containing "github.com" are parsed to extract the user/repo and fetched from GitHub
  - Other URLs are downloaded directly (zip or tar.gz based on URL extension)
  - Local paths are walked to collect matching files
  - Archives with a single common top-level directory have that prefix stripped
  - Only files matching ALLOWED_TOPICS are included in results

  Constraints:
  - Fetch must raise RuntimeError for missing directories, empty archives, or sources with no matching files
  - GitHub repos are tried with "main" branch first, then "master" as fallback

  ## Frozen Examples Rule

  After a feature is BASELINED, all `Example:` blocks are immutable. Changes require
  `@deprecated` on the old Example (preserving the original @id) and a new Example
  with a new @id.

  `@id` tags are for traceability only — do NOT add priority tags to Examples.

  ## Questions

  | ID | Question | Status | Answer / Assumption |
  |----|----------|--------|---------------------|
  | Q1 | Should fetch validate that the archive contains allowed files before returning? | Resolved | Yes — an empty result set after filtering raises RuntimeError |

  ## Changes

  | Session | Q-IDs | Change |
  |---------|-------|--------|
  | 2026-05-02 | Q1 | Created: fetch feature derived from test suite |

  Rule: Local directory fetching
    As a developer
    I want to fetch templates from a local directory
    So that I can test or use custom template sources without a network connection

  @id:fetch-local-directory
    Example: Fetches allowed files from local directory
      Given a local template directory containing AGENTS.md, .opencode/agents/default.md, and src/main.py
      When smith fetches from the local directory
      Then it returns file specs for AGENTS.md and .opencode/agents/default.md
      And it does NOT return src/main.py

  @id:fetch-local-missing
    Example: Raises error for missing directory
      Given a nonexistent path "/nonexistent/path"
      When smith fetches from that path
      Then it raises RuntimeError with "not found"

  @id:fetch-local-no-matching
    Example: Raises error when no files match allowed topics
      Given a local directory containing only README.md (not an allowed topic)
      When smith fetches from that directory
      Then it raises RuntimeError with "No matching files"

  Rule: Archive top-level directory detection
    As a developer
    I want archive entries with a common top-level directory to have that prefix stripped
    So that files are placed at the project root, not nested under the repo folder

  @id:fetch-detect-top-dir
    Example: Strips common top-level directory from archive entries
      Given a zip archive with entries "temple8-main/AGENTS.md" and "temple8-main/.opencode/agents/default.md"
      When smith extracts the archive
      Then file specs have paths "AGENTS.md" and ".opencode/agents/default.md"