# Product Definition: smith

> **Status:** DRAFT (2026-05-01)
> This document is the single source of truth for project scope and conventions.
> Supersedes IN_20260422 — the original product definition captured the wrong product scope.

---

## What smith IS

- An AI pair programming platform that assimilates ordinary projects into high-performing, AI-augmented systems
- A CLI tool (`smith`) that connects standardised agent configurations (AGENTS.md, .opencode/, .templates/, .flowr/) to any project directory — and disconnects cleanly when done
- A standardisation engine: the same agents, the same flows, every project, by connecting once and working immediately
- A demonstration vehicle that ships with four working commands (`connect`, `disconnect`, `update`, `status`) so engineers see the full connect/work/disconnect cycle end-to-end

## What smith IS NOT

- Does NOT execute AI agents — smith configures projects to use AI agents, it doesn't run them
- Does NOT provide CI/CD infrastructure — it doesn't replace your pipelines or deployment setup
- Does NOT manage package dependencies or versions
- Does NOT enforce a specific programming language or framework — smith works with any project
- Does NOT silently overwrite project customizations — user-tracked files are skipped; smith-managed files are auto-updated
- Does NOT leave partial state — connects are atomic: all files or none

## Why does this exist

AI agents need structure. Without consistent agent configurations, each project has different .opencode agents, different workflows, and different templates. Engineers waste time maintaining these across projects. Existing solutions are either bare skeletons or opinionated frameworks. smith fills this gap by providing a standardised, reversible way to connect AI agent configurations to any project — new or legacy — so engineers can focus on building, not configuring. Like Agent Smith in the Matrix, smith enters a project, copies its patterns, and returns something more capable than what it found.

## Users

- **Software Engineer** — runs `smith connect` in any project directory to immediately start working with standard AI agent workflows; runs `smith disconnect` when done
- **Tech Lead** — standardises AI agent configurations across the team's projects by connecting the same template to each one

## Quality Attributes

| Attribute | Scenario | Target | Priority |
|-----------|----------|--------|----------|
| Safety | When smith connects to a project that already has user-tracked agentic files (not managed by smith), it skips user-tracked files; smith-managed files are auto-updated without `--overwrite`. | Zero silent overwrites of user-tracked files, ever | Must (#1) |
| Atomicity | When smith connects, either all agentic files are written or none are | No partial connections, ever | Must (#2) |
| Clean separation | When smith disconnects from a project, no agentic files remain (only .gitignore entries) | Zero orphaned files after disconnect | Must (#3) |
| Usability | When an engineer runs `smith connect` in any project directory, they can immediately start working with standard flows and agents | < 1 minute from connect to working | Must (#4) |
| Modifiability | When a new template source type is needed, it can be added as an infrastructure adapter without changing domain logic | Zero domain changes for new source types | Should (#5) |
| Testability | When unit tests run, domain logic can be tested via port mocks without filesystem or network access | 100% domain test coverage without infrastructure | Should (#6) |

---

## Out of Scope

- AI execution engine (smith configures agents, doesn't run them)
- CI/CD infrastructure
- Package management
- Language/framework enforcement
- IDE-specific configuration

## Delivery Order

1 → **smith-commands** — `smith connect [--from <path/url>]`, `smith disconnect`, `smith update`, `smith status`. Four commands that demonstrate the full connect/work/disconnect cycle end-to-end. This feature validates the entire workflow and serves as the reference implementation for future features.

---

## Project Conventions

### Definition of Done

All criteria must be met before a feature is considered done.

**Development:**

- [ ] All BDD scenarios from `features/smith-commands.feature` pass
- [ ] Quality Gate passes all three tiers (Design → Structure → Conventions)
- [ ] Test coverage meets project threshold (≥ 80%)
- [ ] No test coupling — tests verify behavior, not structure
- [ ] Production code follows priority order: YAGNI > DRY > KISS > OC > SOLID > Design Patterns
- [ ] Code uses ubiquitous language from glossary.md (Connection, FileSpec, TemplateSource, GitignoreSection, ConnectionStatus)
- [ ] Safety invariant verified: no silent overwrites of user-tracked files in any code path (all Must Examples in Rule 2 pass)
- [ ] Atomicity invariant verified: pair-atomic write (AGENTS.md + .opencode/) tested with rollback (SC-008)
- [ ] Clean separation invariant verified: disconnect removes all managed files, preserves user-tracked files (SC-014, SC-017)
- [ ] Exit codes verified: 0 (success), 1 (error) — all Examples assert correct exit code

**Review — Tier 1: Design Correctness (does it do the right thing?)**

- [ ] Domain invariants enforced: Safety (user-tracked files are never overwritten; smith-managed files are auto-updated), Atomicity (pair-atomic writes), Clean separation (no orphaned files)
- [ ] All ports are Protocol interfaces in the domain layer; no infrastructure imports in domain or application
- [ ] Connection aggregate is the sole entry point for all four commands
- [ ] CLI is a thin delivery adapter that delegates to application use cases

**Review — Tier 2: Test Structure (are tests good enough?)**

- [ ] Each Must Example has a passing test with observable outcome
- [ ] Tests mock ports (FileSystemPort, GitignorePort, TemplateSourcePort) — no filesystem/network in unit tests
- [ ] SC-008 (pair-atomic rollback) has a test that simulates mid-write failure
- [ ] User-tracked file skipping tested for each managed file type
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

### Branch Strategy

- **Convention:** Trunk-based (short-lived feature branches from trunk, PR before merge)
- **Branch naming:** `<type>/<short-description>` (e.g., `feature/add-smith-commands`)
- **Merge policy:** Squash merge to trunk after approval

### Naming

- **CLI command:** `smith`
- **PyPI package:** `agents-smith`
- **Python module: `smith``
- **Tagline:** Pair program with AI, the right way.
- **Branding:** Matrix/Agent Smith theme (see `docs/branding.md`)

### .gitignore Convention

smith manages its own section in .gitignore, marked with `# smith managed`. On connect, entries for agentic files are added to this section. On disconnect, the agentic files are removed but the `# smith managed` section is preserved (it serves as a guard for future usage). Files listed in `# smith managed` are treated as managed by smith; files outside this section are user-tracked and never touched by smith.

---

## Scope Changes

| Date | Session | Change | Reason |
|------|---------|--------|--------|
| 2026-05-01 | IN_20260501_stakeholder-reinterview | Complete product redefinition: smith is an AI pair programming platform, not just a Python template. Delivery order changed from cli-entrypoint to smith-commands. | Stakeholder clarified product scope during reinterview |