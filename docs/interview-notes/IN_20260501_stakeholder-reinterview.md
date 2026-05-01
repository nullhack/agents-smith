# IN_20260501_stakeholder-reinterview — Corrected product scope discovery

> **Status:** COMPLETE
> **Interviewer:** PO
> **Participant(s):** Stakeholder
> **Session type:** Scope refinement (replaces IN_20260422 which captured the wrong product)

---

## General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | Who are the users? | Software engineers/developers who work on multiple projects and want consistent AI-assisted workflows across all of them. |
| Q2 | What does the product do at a high level? | smith is an AI pair programming platform that assimilates ordinary projects into high-performing, AI-augmented systems. It connects standardised agent configurations (AGENTS.md, .opencode/, .templates/, .flowr/) to any project, enabling consistent AI-assisted workflows. Like Agent Smith in the Matrix, smith takes control of a project — then detaches when done. |
| Q3 | Why does it exist — what problem does it solve? | AI agents need structure. Without consistent agent configurations, each project has different .opencode agents, different workflows, and different templates. Engineers waste time maintaining these across projects. smith standardises the AI agent experience — connect, work, detach — the same agents, the same flows, every project. |
| Q4 | When and where is it used? | Anytime — plug in or out as needed. Works on any project directory, even legacy ones. Not limited to project inception. |
| Q5 | Success — what does "done" look like? | A uniform experience across projects: `smith connect` in any directory and you're immediately working with standard flows and agents. `smith disconnect` and the project is clean (no agentic files left, only .gitignore entries). Customisation is per-template: use `--from <path/url>` for a different agent template. |
| Q6 | Failure — what must never happen? | Destructive overwrites without explicit `--overwrite` flag. Rigid workflows that don't adapt to different projects. Complex connect/disconnect workflows. Partial connections — smith must either connect fully or write no files at all (atomic). Never silently overwrite customizations. |
| Q7 | Out-of-scope — what are we explicitly not building? | AI execution engine (smith configures agents, doesn't run them). CI/CD infrastructure. Package management. Language/framework enforcement. |

## Connect/Disconnect

| ID | Question | Answer |
|----|----------|--------|
| Q8 | When smith connects, what happens? | `smith connect` copies the default template's agentic files (AGENTS.md, .opencode/, .templates/, .flowr/) into the project directory. `smith connect --from <path/url>` copies from a specified template source instead of the default (agents-smith). |
| Q9 | When smith disconnects, what happens? | Removes agentic files from the project. Keeps .gitignore entries (managed section). If the user wants to push agentic files, they can remove entries from .gitignore. Disconnect means "I don't want the files here anymore" — if they want to continue with the files, they wouldn't call disconnect. |
| Q10 | How does --overwrite work? | smith refuses to connect if agentic files already exist (must disconnect first), unless `--overwrite` is explicitly passed. Destructive overwrites are only possible when the stakeholder forces it. |
| Q11 | How does smith handle .gitignore? | smith manages its own section in .gitignore, marked with a comment like `# smith managed`. On connect, it adds entries for the agentic files. On disconnect, it removes those entries (unless the user has removed them manually to push the files). |
| Q12 | Which agentic files get connected? | AGENTS.md, .opencode/, .templates/, .flowr/ — these four items are the standard set that smith connects to a project. |

## Conflict Handling

| ID | Question | Answer |
|----|----------|--------|
| Q13 | What if AGENTS.md or .opencode/ already exist in the project? | Warn and refuse to overwrite unless `--overwrite` is passed. These are core agent configs and should not be silently replaced. |
| Q14 | What if .flowr/ or .templates/ already exist? | Needs architect decision. Projects may have their own .flowr and .templates specific to that project. We should not overwrite those if already existing, but the user may want to override. The exact merge/replacement strategy needs architectural input. |

## Naming and Branding

| ID | Question | Answer |
|----|----------|--------|
| Q15 | What are the CLI and package names? | CLI command: `smith`. PyPI package: `agents-smith`. The branding uses the Matrix/Agent Smith theme from the official remote repo (https://github.com/nullhack/agents-smith). The local branding file is stale and wrong — it still has the old agents-smith/Greek theme. Must be replaced with the remote version. |

## Template Source

| ID | Question | Answer |
|----|----------|--------|
| Q16 | What is the relationship between smith and agents-smith? | Agents-Smith is the default template. `smith connect` uses agents-smith's agentic files by default. `smith connect --from <path/url>` uses a different template source. |
| Q17 | How does multi-project support work? | Each project gets its own copy of the agentic files. `smith connect` copies files into the project directory. The same template can be connected to multiple projects independently. `smith update` refreshes a project's agentic files from the source template. |

## Feature: smith-commands

| ID | Question | Answer |
|----|----------|--------|
| Q18 | What CLI commands should smith support? | Four commands: `smith connect [--from <path/url>]`, `smith disconnect`, `smith update`, `smith status`. All four are needed for the first feature to demonstrate the full connect/work/disconnect cycle end-to-end. |
| Q19 | Which commands go in the first feature? | All four — connect, disconnect, update, and status — as the single demonstration feature. |

---

## Quality Attributes

| ID | Attribute | Scenario | Target | Priority |
|----|-----------|----------|--------|----------|
| QA1 | Usability | When an engineer runs `smith connect` in any project directory, they can immediately start working with standard flows and agents | < 1 minute from connect to working | Must |
| QA2 | Safety | When smith connects to a project that already has agentic files, it refuses to overwrite without explicit `--overwrite` flag | Zero silent overwrites, ever | Must |
| QA3 | Clean separation | When smith disconnects from a project, no agentic files remain (only .gitignore entries) | Zero orphaned files after disconnect | Must |
| QA4 | Atomicity | When smith connects, either all agentic files are written or none are | No partial connections, ever | Must |

---

## Pain Points Identified

- Maintaining different .opencode agents and workflows across multiple projects is wasteful and inconsistent
- AI agents lack structure — each project reinvents agent configs from scratch
- No standardised way to "plug in" AI-assisted workflows to existing/legacy projects

## Business Goals Identified

- Uniform AI agent experience across all projects
- Instant setup — connect and go within minutes
- Clean connect/disconnect cycle — projects should be transformable and reversible

## Terms to Define (for glossary)

- connect — smith command that copies agentic files into a project directory
- disconnect — smith command that removes agentic files from a project directory
- agentic files — the set of files smith manages: AGENTS.md, .opencode/, .templates/, .flowr/
- template source — the origin of agentic files (default: agents-smith; override with --from)
- assimilate — smith's core metaphor: enter a project, configure it with standard AI agents, transform it
- managed .gitignore section — a marked block in .gitignore that smith creates and maintains

## Action Items

- [ ] Architect to decide merge/overwrite strategy for .flowr/ and .templates/ when they already exist in a project
- [ ] Replace local branding.md with the remote version (Matrix/Agent Smith theme)
- [ ] Replace local logo.svg and banner.svg with remote versions
- [ ] Retire or archive the old IN_20260422 interview notes (captured wrong product scope)