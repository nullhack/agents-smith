# Discovery Journal: smith

---

## 2026-04-20 — Session 1
Status: IN-PROGRESS

### General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | Who are the users? | Python developers starting or improving their Python projects |
| Q2 | What does the product do at a high level? | CLI tool with two commands: `smith init <name>` creates a new project using `uv init` then layers template add-ons on top; `smith assimilate` applies template structure/tooling to an existing project |
| Q3 | Why does it exist — what problem does it solve? | Solves the problem of having a proper production-grade project setup and being able to update/upgrade it later |
| Q4 | When and where is it used? | CLI tool used locally; two modes: create new project, or apply template to existing project |
| Q5 | Success — what does "done" look like? | New project runs straightaway after creation; existing project is upgraded without affecting existing content |
| Q6 | Failure — what must never happen? | Destroys anything in an existing project; spawns a project that doesn't work as intended |
| Q7 | Out-of-scope — what are we explicitly not building? | Running the project (smith only sets up), version-tracking template updates, managing multiple projects, publishing to PyPI, IDE/editor integration |

### Cross-cutting: Commands

| ID | Question | Answer |
|----|----------|--------|
| Q8 | What is the second command word? | `assimilate` — Matrix-branded, fits the Agent Smith aesthetic |
| Q9 | Are these two separate commands or one command with a flag? | Two separate commands: `smith init <name>` and `smith assimilate` |
| Q10 | What does `smith init` actually do? | Runs `uv init` then layers template add-ons on top — NOT a git clone of the template |
| Q11 | For `smith assimilate` — what does it touch? | `.opencode/` folder (skills, agents, prompts), `pyproject.toml` additions (merge/add missing, don't overwrite existing), CI files (`.github/workflows/`), folder structure (create `docs/`, `tests/` if missing), `AGENTS.md` |

### Cross-cutting: Safety

| ID | Question | Answer |
|----|----------|--------|
| Q12 | What happens if `smith init` is run in a directory that already exists? | Prompt per conflicting file: skip / overwrite / show diff |
| Q13 | What happens if `smith assimilate` is run twice on the same project? | Safe to run again — always prompts on conflicts; idempotent by design |
| Q14 | Is there a dry-run or preview mode? | Yes — show what would change before writing anything |

### Cross-cutting: Configuration

| ID | Question | Answer |
|----|----------|--------|
| Q15 | Does the user provide project metadata during creation? | Yes — interactive prompts during creation (name, author, GitHub username, etc.) that substitute placeholders in template files |

### Out-of-scope

| ID | Question | Answer |
|----|----------|--------|
| Q17 | Is smith responsible for running the project after setup? | No — smith only creates/upgrades; running is out of scope |
| Q18 | Should smith update an already-applied template to a newer version? | No — version-tracking template updates is out of scope |
| Q19 | Should smith manage multiple projects? | No — one project at a time; multi-project management is out of scope |

Status: COMPLETE

---

## 2026-04-20 — Session 2
Status: IN-PROGRESS

### Refinements and Baseline Approval

| ID | Question | Answer |
|----|----------|--------|
| Q20 | What is the final command name for project creation? | `smith new` (changed from `smith init`) — command is `smith new <name> [path]` |
| Q21 | How is the template distributed? | As a uv GitHub dependency pinned by commit `rev` in `pyproject.toml`; no runtime download — smith reads template files from the installed package |
| Q22 | Does `smith assimilate` accept a path argument? | Yes — `smith assimilate [path]`, defaults to cwd if no path given |
| Q23 | Has the stakeholder approved both features for baselining? | Yes — both `smith-new` and `smith-assimilate` are approved for baselining as of 2026-04-20 |

Status: COMPLETE
