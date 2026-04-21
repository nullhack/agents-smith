Feature: smith assimilate

  Applies the nullhack/python-project-template structure and tooling to an existing
  Python project. The template is bundled as a uv GitHub dependency (pinned by commit
  rev) — no runtime download occurs. Touches: `.opencode/` (skills, agents, prompts),
  `pyproject.toml` (merges missing entries only, never overwrites existing),
  `.github/workflows/` CI files, `docs/` and `tests/` folders (created if missing), and
  `AGENTS.md`. Supports a `--dry-run` flag that shows all planned changes without writing
  any files. Conflict resolution is per-file (skip / overwrite / diff). Safe to run
  multiple times — always prompts on conflicts.

  Status: BASELINED (2026-04-20)

  Rules (Business):
  - Applies template add-ons to an existing project without destroying existing content
  - `pyproject.toml` entries are merged: missing entries are added, existing entries are never overwritten
  - Folder structure additions (`docs/`, `tests/`) are created only if missing
  - Conflict resolution is per-file: user chooses skip, overwrite, or view diff
  - `--dry-run` flag shows all planned changes without writing any files
  - Operation is idempotent: running `smith assimilate` again is safe and always prompts on conflicts
  - Template source: nullhack/python-project-template installed as uv GitHub dependency (rev-pinned)

  Constraints:
  - Entry point: `smith assimilate [path]` CLI command; defaults to cwd if no path given
  - Must never delete or overwrite files without explicit user confirmation
  - Template source: nullhack/python-project-template installed as uv GitHub dependency

  Rule: Template application
    As a Python developer
    I want to run `smith assimilate` on an existing project
    So that I get the template tooling without recreating the project from scratch

    @id:a1b2c3d4
    Example: Template files are added to an existing project
      Given an existing Python project at the target path that lacks `.opencode/` and `AGENTS.md`
      When the developer runs `smith assimilate` and confirms all prompts
      Then `.opencode/`, `AGENTS.md`, `.github/workflows/`, `docs/`, and `tests/` are present in the project

    @id:e5f6a7b8
    Example: Existing project files are not deleted
      Given an existing Python project with files not part of the template
      When the developer runs `smith assimilate` and confirms all prompts
      Then all pre-existing project files remain present and unmodified

  Rule: Safe pyproject.toml merge
    As a Python developer
    I want missing pyproject.toml entries added without touching existing ones
    So that my existing configuration is preserved

    @id:9c0d1e2f
    Example: Missing pyproject.toml entries are added
      Given an existing `pyproject.toml` that lacks template-required entries
      When the developer runs `smith assimilate`
      Then the missing entries are added to `pyproject.toml`

    @id:3f4a5b6c
    Example: Existing pyproject.toml entries are never overwritten
      Given an existing `pyproject.toml` with a `[project.name]` entry set to "my-existing-name"
      When the developer runs `smith assimilate`
      Then `[project.name]` remains "my-existing-name" after assimilation

  Rule: Dry-run preview
    As a Python developer
    I want to preview all planned changes before they are written
    So that I can decide whether to proceed without risk of accidental overwrites

    @id:7d8e9f0a
    Example: Dry-run shows planned changes without writing files
      Given an existing project that would receive template add-ons
      When the developer runs `smith assimilate --dry-run`
      Then a list of all files that would be added or modified is displayed and no files are written

    @id:b1c2d3e4
    Example: Dry-run on an up-to-date project reports no changes
      Given an existing project that already has all template add-ons applied
      When the developer runs `smith assimilate --dry-run`
      Then smith reports that no changes would be made

  Rule: Per-file conflict resolution
    As a Python developer
    I want to choose skip, overwrite, or diff for each conflicting file
    So that I have full control over what gets changed in my existing project

    @id:f5a6b7c8
    Example: Conflicting file triggers a per-file prompt
      Given a template file already exists in the target project with different content
      When the developer runs `smith assimilate`
      Then smith prompts the user for that file with options: skip, overwrite, diff

    @id:d9e0f1a2
    Example: Choosing skip leaves the existing file unchanged
      Given a conflict prompt is shown for an existing file during assimilation
      When the developer chooses "skip"
      Then the existing file is left unchanged and smith continues to the next file

    @id:b3c4d5e6
    Example: Choosing overwrite replaces the existing file with the template version
      Given a conflict prompt is shown for an existing file during assimilation
      When the developer chooses "overwrite"
      Then the existing file is replaced with the template version

    @id:f7a8b9c0
    Example: Choosing diff shows a unified diff before re-prompting
      Given a conflict prompt is shown for an existing file during assimilation
      When the developer chooses "diff"
      Then a unified diff of the existing file vs the template version is displayed and the prompt is shown again

  Rule: Idempotent operation
    As a Python developer
    I want to run `smith assimilate` multiple times safely
    So that re-running it never silently overwrites my work

    @id:d1e2f3a4
    Example: Re-running assimilate on an already-assimilated project prompts on conflicts
      Given a project that has already had `smith assimilate` applied
      When the developer runs `smith assimilate` again
      Then smith prompts for any conflicting files and makes no changes without explicit confirmation
