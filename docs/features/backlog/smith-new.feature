Feature: smith new

  Creates a new Python project by running `uv init <name>` and then layering
  nullhack/python-project-template add-ons on top. The template is bundled as a uv
  GitHub dependency (pinned by commit rev) — no runtime download occurs. The user is
  prompted interactively for project metadata (name, author, GitHub username, email,
  description), which are substituted into template placeholders. The resulting project
  is immediately runnable. If the target directory already exists, conflicts are resolved
  per-file via prompt (skip / overwrite / diff).

  Status: BASELINED (2026-04-20)

  Rules (Business):
  - Project is created using `uv init` as the foundation, not by cloning the template repo
  - Template add-ons are read from the installed nullhack/python-project-template package (uv GitHub dep, rev-pinned)
  - User is prompted interactively for: project name, author, GitHub username, email, description
  - Metadata placeholders in template files are substituted with user-provided values
  - If the target directory already exists, conflicts are resolved per-file: skip / overwrite / diff
  - The resulting project must be immediately runnable after creation

  Constraints:
  - Entry point: `smith new <name> [path]` CLI command
  - Requires `uv` to be available on the system PATH
  - Template source: nullhack/python-project-template installed as uv GitHub dependency

  Rule: Project scaffolding
    As a Python developer
    I want to run `smith new <name>` to create a new project
    So that I get a production-ready project structure without manual setup

    @id:c1a2b3d4
    Example: New project directory is created with uv init structure
      Given no directory named "myproject" exists at the target path
      When the developer runs `smith new myproject`
      Then a directory "myproject" is created containing a uv-initialized project structure

    @id:e5f6a7b8
    Example: Template add-ons are present in the new project
      Given no directory named "myproject" exists at the target path
      When the developer runs `smith new myproject`
      Then the new project contains `.opencode/`, `AGENTS.md`, `.github/workflows/`, `docs/`, and `tests/`

    @id:9c0d1e2f
    Example: Missing uv on PATH produces a clear error
      Given `uv` is not available on the system PATH
      When the developer runs `smith new myproject`
      Then smith exits with a non-zero code and an error message indicating uv is required

  Rule: Metadata substitution
    As a Python developer
    I want to provide my project metadata interactively
    So that template placeholders are replaced with my actual project details

    @id:3f4a5b6c
    Example: User is prompted for all required metadata fields
      Given the developer runs `smith new myproject`
      When smith reaches the metadata collection step
      Then smith prompts for: project name, author name, GitHub username, email, and description

    @id:7d8e9f0a
    Example: Placeholders in template files are replaced with provided metadata
      Given the developer provides name "myproject", author "Alice", GitHub username "alice", email "alice@example.com", description "My project"
      When smith applies the template add-ons
      Then all placeholder tokens in template files are replaced with the corresponding provided values

    @id:b1c2d3e4
    Example: Empty required metadata field is rejected
      Given the developer leaves a required metadata field blank
      When smith processes the metadata input
      Then smith re-prompts for the blank field with a message indicating it is required

  Rule: Conflict resolution on existing directory
    As a Python developer
    I want to be prompted per-file when the target directory already exists
    So that I can choose to skip, overwrite, or diff each conflicting file without losing existing work

    @id:f5a6b7c8
    Example: Existing directory triggers per-file conflict prompt
      Given a directory "myproject" already exists at the target path with existing files
      When the developer runs `smith new myproject`
      Then smith prompts the user for each conflicting file with options: skip, overwrite, diff

    @id:d9e0f1a2
    Example: Choosing skip leaves the existing file unchanged
      Given a conflict prompt is shown for an existing file
      When the developer chooses "skip"
      Then the existing file is left unchanged and smith continues to the next file

    @id:b3c4d5e6
    Example: Choosing overwrite replaces the existing file with the template version
      Given a conflict prompt is shown for an existing file
      When the developer chooses "overwrite"
      Then the existing file is replaced with the template version

    @id:f7a8b9c0
    Example: Choosing diff shows a unified diff before re-prompting
      Given a conflict prompt is shown for an existing file
      When the developer chooses "diff"
      Then a unified diff of the existing file vs the template version is displayed and the prompt is shown again

  Rule: Runnable result
    As a Python developer
    I want the created project to be immediately runnable
    So that I can start working without additional setup steps

    @id:d1e2f3a4
    Example: New project passes its own test suite immediately after creation
      Given the developer runs `smith new myproject` and provides all metadata
      When the developer runs `uv run task test-fast` inside the new project directory
      Then all tests pass with no configuration required
