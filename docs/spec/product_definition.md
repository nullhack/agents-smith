# Product Definition: smith

> **Status:** DRAFT (2026-05-02)
> This document is the single source of truth for project scope and conventions.
> Derived from working code on the rebuild/minimal-v2 branch.

---

## What smith IS

- A CLI tool (`smith`) that clones standardised agent configurations (AGENTS.md, .opencode/, .flowr/, .templates/) to any project directory — and purges cleanly when done
- A template fetcher that resolves template sources from GitHub repos, HTTP URLs, or local directories, filtering files through an allowed-topics safety boundary
- A .gitignore manager that tracks which files smith installed in a delimited section, enabling clean purging with zero orphaned files
- Like Agent Smith in the Matrix, smith enters a project, copies its patterns, and returns something more capable than what it found

## What smith IS NOT

- Does NOT execute AI agents — smith configures projects to use AI agents, it doesn't run them
- Does NOT provide CI/CD infrastructure — it doesn't replace your pipelines or deployment setup
- Does NOT manage package dependencies or versions
- Does NOT enforce a specific programming language or framework — smith works with any project
- Does NOT silently overwrite project files — existing directories are skipped unless `--overwrite` is passed; the allowed-topics filter ensures only agentic files are ever written
- Does NOT leave partial state — clone writes files and updates .gitignore together; purge removes all managed files listed in .gitignore

## Why does this exist

AI agents need structure. Without consistent agent configurations, each project has different .opencode agents, different workflows, and different templates. Engineers waste time maintaining these across projects. Existing solutions are either bare skeletons or opinionated frameworks. smith fills this gap by providing a standardised, reversible way to clone AI agent configurations to any project — new or legacy — so engineers can focus on building, not configuring.

## Users

- **Software Engineer** — runs `smith clone` in any project directory to immediately start working with standard AI agent workflows; runs `smith purge` when done
- **Tech Lead** — standardises AI agent configurations across the team's projects by cloning the same template to each one

## Quality Attributes

| Attribute | Scenario | Target | Priority |
|-----------|----------|--------|----------|
| Reliability | When clone runs, only allowed topic files (AGENTS.md, .opencode/, .flowr/, .templates/) are written | Zero disallowed files written, ever | Must (#1) |
| Reversibility | When purge runs, all smith-managed files are removed and no other files are affected | Zero non-managed files deleted, ever | Must (#2) |
| Safety | When clone runs on a project that already has smith-managed directories, existing content is preserved without --overwrite | Zero silent overwrites of existing files | Must (#3) |
| Usability | When an engineer runs `smith clone` without arguments, it resolves the source from pyproject.toml or defaults | Correct source resolved without manual configuration | Should (#4) |
| Modifiability | When a new template source type is needed, it can be added to the fetch function without changing clone/purge logic | Zero changes to clone/purge for new source types | Should (#5) |

---

## Out of Scope

- AI execution engine (smith configures agents, doesn't run them)
- CI/CD infrastructure
- Package management
- Language/framework enforcement
- Update or status commands (current scope: clone and purge only)
- Atomic file writes via temp-directory staging (current implementation writes directly)
- Source metadata in .gitignore section headers (current implementation tracks patterns only)

## Delivery Order

1 → **smith-clone-purge** — `smith clone [--source <path/url>] [--overwrite]`, `smith purge`. Two commands that demonstrate the clone/purge cycle end-to-end. This feature validates the core workflow: resolve source, fetch files, filter by allowed topics, write to project, track in .gitignore, and cleanly remove on purge.

---

## Project Conventions

### Definition of Done

All criteria must be met before a feature is considered done.

**Development:**

- [ ] All BDD scenarios from feature files pass
- [ ] Quality Gate passes all three tiers (Design → Structure → Conventions)
- [ ] Test coverage meets project threshold (≥ 80%)
- [ ] No test coupling — tests verify behavior, not structure
- [ ] Production code follows priority order: YAGNI > DRY > KISS > OC > SOLID > Design Patterns
- [ ] Code uses ubiquitous language from glossary.md
- [ ] Reliability invariant verified: no disallowed files written in any code path
- [ ] Reversibility invariant verified: purge removes only managed files
- [ ] Safety invariant verified: no silent overwrites without --overwrite flag
- [ ] Exit codes verified: 0 (success), 1 (error) — all Examples assert correct exit code

**Review — Tier 1: Design Correctness (does it do the right thing?)**

- [ ] Domain invariants enforced: Reliability (only allowed topics written), Reversibility (only managed files removed), Safety (existing files skipped without --overwrite)
- [ ] Allowed-topics filter is applied at every code path that writes files
- [ ] .gitignore section management is idempotent — add/replace works correctly
- [ ] Source resolution chain (CLI arg > pyproject.toml > default) is followed consistently

**Review — Tier 2: Test Structure (are tests good enough?)**

- [ ] Each Must Example has a passing test with observable outcome
- [ ] Tests cover all three source types (github:, http, local)
- [ ] Tests cover overwrite and non-overwrite paths
- [ ] Tests cover .gitignore section management (add, replace, has_section, get_patterns)
- [ ] No test couples to implementation details (private methods, file paths, internal state)

**Review — Tier 3: Conventions (does it follow project standards?)**

- [ ] CI pipeline passes all checks
- [ ] Code Review approved by R (independent reviewer, not the SE who wrote the code)
- [ ] Acceptance Testing passed — PO verifies BDD scenarios behave as expected
- [ ] `smith` CLI command works (`python -m smith` entry point)
- [ ] `--help` and `--version` flags work

**Deployment:**

- [ ] Release Verification checklist completed
- [ ] CHANGELOG.md updated with delivered scenarios

### Deployment

**Deployment type:** Library (installable Python package)

**CLI command:** `smith` (entry point: `python -m smith`)
**PyPI package:** `agents-smith`

#### Common (all deployment types)

- [ ] Version bumped in pyproject.toml
- [ ] CHANGELOG.md updated with version and delivered scenarios
- [ ] Git tag created (format: `v<semver>`)

#### Library

- [ ] Package builds without errors (`python -m build`)
- [ ] Package published to PyPI (`twine upload dist/*`)
- [ ] Installable from PyPI in clean environment

#### Rollback Plan

- Revert the git tag and re-publish the previous version to PyPI
- PyPI does not support deleting versions; yank the release instead (`twine upload --yank`)
- Since smith is stateless (no database, no side effects beyond filesystem writes), users can also run `smith purge` to remove all managed files

### Branch Strategy

- **Convention:** Trunk-based (short-lived feature branches from trunk, PR before merge)
- **Branch naming:** `<type>/<short-description>` (e.g., `feature/add-overwrite-flag`)
- **Merge policy:** Squash merge to trunk after approval

### Naming

- **CLI command:** `smith`
- **PyPI package:** `agents-smith`
- **Python module:** `smith`
- **Tagline:** Clone AI agent configurations to any project
- **Branding:** Matrix/Agent Smith theme (see `docs/branding/branding.md`)

### .gitignore Convention

smith manages its own section in .gitignore, marked with `# smith managed` and `# end smith managed`. On clone, entries for agentic files are added to this section. On purge, the agentic files are removed but the `# smith managed` section is preserved (it serves as a guard for future usage). Files listed in `# smith managed` are treated as managed by smith; files outside this section are user-tracked and never touched by smith.

---

## Scope Changes

| Date | Session | Change | Reason |
|------|---------|--------|--------|
| 2026-05-02 | initial | Product definition derived from working code | Baseline from existing implementation on rebuild/minimal-v2 branch |