# Discovery: smith

---

## Session: 2026-04-20

### Context
`smith` is a CLI tool for Python developers who want a production-grade project setup without manual scaffolding. It solves the problem of bootstrapping and maintaining a consistent project structure aligned with the nullhack/python-project-template. Users are developers starting new projects or upgrading existing ones. Success means a new project runs immediately after creation, and an existing project gains template tooling without losing any existing content. Failure means data loss in an existing project or a broken new project. Out of scope: running projects, version-tracking template updates, multi-project management, PyPI publishing, and IDE integration.

### Feature List
- `smith-init` — creates a new Python project using `uv init` then layers template add-ons with interactive metadata prompts
- `smith-assimilate` — applies template structure/tooling to an existing project with per-file conflict resolution and dry-run mode

### Domain Model
| Type | Name | Description | In Scope |
|------|------|-------------|----------|
| Noun | Project | A Python project directory being created or upgraded | Yes |
| Noun | Template | The nullhack/python-project-template add-ons (`.opencode/`, CI, folder structure, `AGENTS.md`) | Yes |
| Noun | Metadata | User-provided values (name, author, GitHub username) substituted into template placeholders | Yes |
| Noun | ConflictResolution | Per-file user decision when a template file already exists: skip, overwrite, or diff | Yes |
| Noun | DryRun | A preview mode that shows planned changes without writing any files | Yes |
| Verb | init | Create a new project via `uv init` then apply template add-ons | Yes |
| Verb | assimilate | Apply template add-ons to an existing project | Yes |
| Verb | merge | Add missing `pyproject.toml` entries without overwriting existing ones | Yes |
| Verb | prompt | Ask the user for metadata or conflict resolution decisions interactively | Yes |

---

## Session: 2026-04-20 (Session 2)

### Feature List
- `smith-new` — renamed from `smith-init`; command confirmed as `smith new <name> [path]`; template source confirmed as uv GitHub dependency pinned by rev
- `smith-assimilate` — path argument confirmed (`smith assimilate [path]`, defaults to cwd); both features baselined

### Domain Model
| Type | Name | Description | In Scope |
|------|------|-------------|----------|
| Noun | TemplateDependency | The nullhack/python-project-template installed as a uv GitHub dep, rev-pinned in pyproject.toml | Yes |
| Verb | new | Create a new project via `uv init` then apply template add-ons | Yes |
