<div align="center">

<img src="docs/assets/banner.svg" alt="agents-smith" width="100%"/>

<br/><br/>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?style=for-the-badge)](https://nullhack.github.io/agents-smith/coverage/)
[![CI](https://img.shields.io/github/actions/workflow/status/nullhack/agents-smith/ci.yml?style=for-the-badge&label=CI)](https://github.com/nullhack/agents-smith/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.13-blue?style=for-the-badge)](https://www.python.org/downloads/)

**Pair program with AI, the right way.**

</div>

---

smith is an AI pair programming platform that connects standardised agent configurations to any project directory — and disconnects cleanly when done. It ships with a complete delivery workflow: structured flows for discovery, planning, TDD development, review, and release, powered by specialised agents (Product Owner, Architect, Engineer, Reviewer, and more).

---

## Install

```bash
pip install agents-smith
```

Or clone for development:

```bash
git clone https://github.com/nullhack/agents-smith
cd agents-smith
curl -LsSf https://astral.sh/uv/install.sh | sh  # skip if uv is already installed
uv sync --all-extras
```

---

## Usage

### Connect

Write agentic files (agents, skills, knowledge, flows, templates) into any project directory:

```bash
smith connect              # from bundled template (no network needed)
smith connect --from PATH  # from a local directory
smith connect --from URL   # from a remote tarball
smith connect --overwrite  # replace existing smith-managed files
```

### Status

Check what smith has connected to your project:

```bash
smith status           # human-readable output
smith status --json    # machine-readable output
```

### Update

Re-sync agentic files from the connected source:

```bash
smith update               # from the same source used at connect time
smith update --from PATH   # from a different local source
```

### Disconnect

Remove all smith-managed files and gitignore entries. User-tracked files are never touched:

```bash
smith disconnect
```

---

## What you get

When you run `smith connect`, the following is written into your project:

| Path | Contents |
|------|----------|
| `AGENTS.md` | Agent routing, session protocol, artifact conventions |
| `.opencode/agents/` | Agent identity definitions (Product Owner, Architect, Engineer, Reviewer, etc.) |
| `.opencode/skills/` | Step-by-step skill definitions for every workflow state |
| `.opencode/knowledge/` | Curated knowledge files (TDD, DDD, architecture, requirements, design, etc.) |
| `.flowr/flows/` | YAML state machine definitions (delivery, TDD cycle, review gate, setup, etc.) |
| `.templates/` | Artifact templates (ADR, feature files, changelog, interview notes, etc.) |

### Agents

Six specialised agents, each owning a phase of the delivery flow:

| Agent | Role |
|-------|------|
| **Product Owner** | Scope discovery, feature selection, acceptance |
| **Domain Expert** | Ubiquitous language, domain modeling, glossary |
| **Architect** | System design, ADRs, context maps, review |
| **Software Engineer** | TDD implementation, refactoring, merging |
| **Reviewer** | Adversarial review (design, structure, conventions) |
| **Design Agent** | Visual identity, colors, assets |

### Flows

Workflow state machines powered by [flowr](https://pypi.org/project/flowr/):

| Flow | Purpose |
|------|---------|
| `delivery-flow` | End-to-end feature delivery (select → specify → implement → review → accept) |
| `tdd-cycle-flow` | Red-green-refactor loop within a feature |
| `review-gate-flow` | Three-tier review (design → structure → conventions) |
| `setup-project-flow` | Initialise a new project from template |
| `discovery-flow` | Stakeholder interviews and product scoping |
| `planning-flow` | Feature breakdown and BDD specification |
| `architecture-flow` | System design and context mapping |
| `post-mortem-flow` | Incident analysis and lessons |

### Knowledge

Curated research summaries covering TDD, DDD, architecture patterns, SOLID, test design, code review, versioning, and more. Agents load these progressively — key takeaways for quick reference, full documents for detailed work.

---

## Development

```bash
uv run task test              # full suite + coverage
uv run task test-fast         # fast, no coverage (TDD loop)
uv run task lint              # ruff format + check
uv run task static-check      # pyright type checking
uv run task run               # run smith
uv run task doc-build         # build API docs + coverage report
uv run task release-check     # lint + typecheck + test + docs
```

### Updating the bundled template

The `smith/data/` directory ships with a bundled template. To sync it from the upstream [temple8](https://github.com/nullhack/temple8) repository:

```bash
./scripts/update-bundle.sh
```

---

## Documentation

- **[Product Definition](docs/spec/product_definition.md)** — what smith is, who it's for, quality attributes
- **[System Overview](docs/spec/system.md)** — architecture, domain model, module structure, constraints
- **[Glossary](docs/spec/glossary.md)** — living domain glossary
- **[Technical Design](docs/spec/technical_design.md)** — hexagonal architecture, contracts, C4 diagrams
- **[Context Map](docs/spec/context_map.md)** — bounded contexts and integration points
- **[Branding](docs/branding.md)** — visual identity, voice, release naming convention

---

## License

MIT — see [LICENSE](LICENSE).

**Author:** [@nullhack](https://github.com/nullhack) · [Documentation](https://nullhack.github.io/agents-smith)

<!-- MARKDOWN LINKS -->
[contributors-shield]: https://img.shields.io/github/contributors/nullhack/agents-smith.svg?style=for-the-badge
[contributors-url]: https://github.com/nullhack/agents-smith/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/nullhack/agents-smith.svg?style=for-the-badge
[forks-url]: https://github.com/nullhack/agents-smith/network/members
[stars-shield]: https://img.shields.io/github/stars/nullhack/agents-smith.svg?style=for-the-badge
[stars-url]: https://github.com/nullhack/agents-smith/stargazers
[issues-shield]: https://img.shields.io/github/issues/nullhack/agents-smith.svg?style=for-the-badge
[issues-url]: https://github.com/nullhack/agents-smith/issues
[license-shield]: https://img.shields.io/badge/license-MIT-green?style=for-the-badge
[license-url]: https://github.com/nullhack/agents-smith/blob/main/LICENSE