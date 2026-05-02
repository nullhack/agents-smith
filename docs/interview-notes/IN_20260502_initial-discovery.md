# IN_20260502_initial-discovery — Derived from working code

> **Status:** COMPLETE
> **Interviewer:** PO
> **Participant(s):** eol (nullhack@users.noreply.github.com)
> **Session type:** Initial discovery — derived from working code on rebuild/minimal-v2 branch

---

## General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | Who are the users? | Developers who want to add AI agent configurations to projects; project maintainers who want to remove them; template authors who publish agentic file collections |
| Q2 | What does the product do at a high level? | Clones and purges AI agent configuration files (AGENTS.md, .opencode/, .flowr/, .templates/) to any project from a template source |
| Q3 | Why does it exist — what problem does it solve? | Setting up agentic files manually is repetitive, error-prone, and there's no clean way to remove them later. Smith automates both installation and removal |
| Q4 | When and where is it used? | CLI tool, run during project setup or teardown; CI/CD for bootstrapping |
| Q5 | Success — what does "done" look like? | A developer runs one command (`smith clone`) and has all agentic files in their project, tracked in .gitignore; `smith purge` cleanly removes them |
| Q6 | Failure — what must never happen? | Files outside allowed topics must never be written; existing files must never be overwritten without explicit consent |
| Q7 | Out-of-scope — what are we explicitly not building? | Template authoring/validation, agent orchestration, version locking for templates, monorepo support |

## Source Resolution

| ID | Question | Answer |
|----|----------|--------|
| Q8 | How should the template source be determined? | Priority chain: CLI flag > pyproject.toml config > hardcoded default |
| Q9 | What sources should be supported? | GitHub repos (shorthand), HTTP URLs (zip/tar.gz), local directories |
| Q10 | Should the default source be configurable? | Yes, via `[tool.smith] source` in pyproject.toml |

## Clone/Purge

| ID | Question | Answer |
|----|----------|--------|
| Q11 | What files should be installed? | Only AGENTS.md, .opencode/, .flowr/, .templates/ — the four agentic config topics |
| Q12 | What happens if files already exist? | Skip by default; overwrite only with --overwrite flag |
| Q13 | How does purge know what to remove? | Reads the smith-managed section in .gitignore |
| Q14 | Should purge remove the .gitignore section itself? | No — preserve the markers so reclone can update the section |

---

## Quality Attributes

| ID | Attribute | Scenario | Target | Priority |
|----|-----------|----------|--------|----------|
| QA1 | Reliability | When clone runs, only allowed topic files are written | Zero disallowed files written | Must |
| QA2 | Reversibility | When purge runs, all smith-managed files are removed | Zero non-managed files deleted | Must |
| QA3 | Safety | When clone runs on a project with existing files, they are preserved | Existing content unchanged unless --overwrite | Must |
| QA4 | Usability | When a developer runs smith clone without arguments, source resolves correctly | Correct source resolved without manual config | Should |

---

## Pain Points Identified

- Manually copying agentic config files into every new project is tedious and error-prone
- No standard way to track which files came from a template vs. which are project-specific
- No clean uninstall path — removing agent tooling requires remembering every file

## Business Goals Identified

- Zero-config onboarding: `smith clone` works out of the box
- Safe by default: existing files are never overwritten without explicit flag
- Clean removal: `smith purge` removes only smith-managed files

## Terms to Define (for glossary)

- clone, purge, source, FileSpec, allowed topics, smith-managed section, top-level patterns, overwrite

## Action Items

- [x] Derive documentation from working code