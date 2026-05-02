Feature: Allowed Topics Filter

  The system filters all fetched files against a set of allowed topic prefixes (AGENTS.md, .opencode/, .flowr/, .templates/) before writing. This is a safety boundary ensuring only agentic configuration files are ever written to a project, regardless of what the source archive contains.

  Status: BASELINED (2026-05-02)

  Rules (Business):
  - A relative path is allowed if it exactly matches an allowed topic (e.g., AGENTS.md) or starts with an allowed directory prefix followed by / (e.g., .opencode/)
  - Any file not matching an allowed topic is silently excluded from the result set

  Constraints:
  - The allowed topics list is a compile-time constant — it cannot be configured per-project
  - If no files in the source match any allowed topic, fetch raises RuntimeError

  ## Frozen Examples Rule

  After a feature is BASELINED, all `Example:` blocks are immutable. Changes require
  `@deprecated` on the old Example (preserving the original @id) and a new @id.

  `@id` tags are for traceability only — do NOT add priority tags to Examples.

  ## Questions

  | ID | Question | Status | Answer / Assumption |
  |----|----------|--------|---------------------|
  | Q1 | Should users be able to configure which topics are allowed? | Resolved | No — allowed topics are a fixed safety boundary, not a configuration point |

  ## Changes

  | Session | Q-IDs | Change |
  |---------|-------|--------|
  | 2026-05-02 | Q1 | Created: allowed topics filter feature derived from test suite |

  Rule: Path matching
    As a developer
    I want only allowed topic files to pass through the filter
    So that random files from the source (e.g., README.md, src/) are never written to my project

  @id:allowed-topics-exact-match
    Example: Exact match on AGENTS.md
      Given a relative path "AGENTS.md"
      When the filter checks if it is allowed
      Then it returns true

  @id:allowed-topics-directory-prefix
    Example: Directory prefix match on .opencode/
      Given a relative path ".opencode/agents/default.md"
      When the filter checks if it is allowed
      Then it returns true

  @id:allowed-topics-rejects-random
    Example: Rejects files outside allowed topics
      Given a relative path "README.md"
      When the filter checks if it is allowed
      Then it returns false

  @id:allowed-topics-rejects-src
    Example: Rejects src/ directory
      Given a relative path "src/main.py"
      When the filter checks if it is allowed
      Then it returns false