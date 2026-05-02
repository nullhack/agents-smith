Feature: Source Resolution

  The system resolves the template source from the CLI flag, pyproject.toml config, or a default value. This determines where template files are fetched from during clone.

  Status: BASELINED (2026-05-02)

  Rules (Business):
  - Source resolution follows a strict priority: CLI flag > pyproject.toml [tool.smith] source key > default (github:nullhack/temple8)
  - The source string is passed directly to the fetch function without modification after resolution

  Constraints:
  - Source resolution must complete without network calls
  - An invalid or unreachable source is detected at fetch time, not resolution time

  ## Frozen Examples Rule

  After a feature is BASELINED, all `Example:` blocks are immutable. Changes require
  `@deprecated` on the old Example (preserving the original @id) and a new Example
  with a new @id.

  `@id` tags are for traceability only — do NOT add priority tags to Examples.

  ## Questions

  | ID | Question | Status | Answer / Assumption |
  |----|----------|--------|---------------------|
  | Q1 | Should resolution fail if pyproject.toml exists but has no [tool.smith] section? | Resolved | No — it falls through to default |

  ## Changes

  | Session | Q-IDs | Change |
  |---------|-------|--------|
  | 2026-05-02 | Q1 | Created: source resolution feature derived from test suite |

  Rule: CLI flag takes precedence
    As a developer
    I want the --source CLI flag to override any configured or default source
    So that I can explicitly control which template source is used

  @id:source-resolution-cli-flag
    Example: CLI flag overrides pyproject.toml config
      Given a project with [tool.smith] source = "github:myorg/templates" in pyproject.toml
      When the developer runs smith clone --source github:other/repo
      Then the source resolves to "github:other/repo"

  Rule: Config file fallback
    As a developer
    I want the system to read the source from pyproject.toml when no CLI flag is provided
    So that I can configure a default source for my project

  @id:source-resolution-config-fallback
    Example: Reads source from pyproject.toml
      Given a project with [tool.smith] source = "github:myorg/templates" in pyproject.toml
      When the developer runs smith clone without --source
      Then the source resolves to "github:myorg/templates"

  Rule: Default source
    As a developer
    I want the system to use a default source when no CLI flag or config is present
    So that I can run smith clone without any setup

  @id:source-resolution-default
    Example: Falls back to default when no config exists
      Given a project with no [tool.smith] section in pyproject.toml
      When the developer runs smith clone without --source
      Then the source resolves to "github:nullhack/temple8"