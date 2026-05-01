# Agents-Smith

## Project Structure
- `.flowr/flows/` — YAML state machine definitions (source of truth for routing)
- `.flowr/sessions/` — runtime session state
- `.templates/` — artifact templates (strip `.templates/` prefix and `.template` suffix → destination path)
- `.opencode/` — agents, skills, and knowledge

## Artifact Templates

When creating a document, use the template in `.templates/` that matches the artifact type. Strip the `.templates/` prefix and `.template` suffix to determine the destination path. For example:
- `.templates/docs/adr/ADR_YYYYMMDD_<slug>.md.template` → `docs/adr/ADR_20260430_my-decision.md`
- `.templates/docs/features/feature.feature.template` → `docs/features/my-feature.feature`
- `.templates/docs/interview-notes/IN_YYYYMMDD_<slug>.md.template` → `docs/interview-notes/IN_20260430_session-management.md`

If no template exists for an artifact type, create the document without one.

## Knowledge Resolution
`[[domain/concept]]` → `.opencode/knowledge/{domain}/{concept}.md`

### Progressive Knowledge Loading

Knowledge files use 4-section progressive disclosure. Choose the level that matches the task depth:

| Fragment | Loads | When to Use |
|----------|-------|-------------|
| `#key-takeaways` | Frontmatter + Key Takeaways | Quick reference or reminders when knowledge is already familiar |
| `#concepts` | Frontmatter + Key Takeaways + Concepts | Understanding concepts without detailed examples or procedures |
| (no fragment) | Entire file | Performing evaluation, review, or implementation that needs detection heuristics, examples, tables, and procedures |

**Rule of thumb:** If the agent needs to **find violations, detect patterns, or apply detailed criteria**, load the full document. If it only needs to **recall a principle or definition**, `#key-takeaways` is sufficient.

### Extraction Commands

```bash
sed '/^## Concepts/Q' file.md    # Frontmatter + Key Takeaways only
sed '/^## Content/Q' file.md     # Frontmatter + Key Takeaways + Concepts
cat file.md                       # Full document
```

Examples:
- `[[requirements/invest#key-takeaways]]` — quick reference for INVEST criteria
- `[[requirements/invest#concepts]]` — understanding what each letter means with context
- `[[software-craft/smell-catalogue]]` — full catalogue needed to detect code smells during review

## Discovery
Do not enumerate files — they go stale. Discover what exists at runtime:

```bash
ls .opencode/agents/                    # agent identity definitions
ls .opencode/skills/                    # skill directories (each has SKILL.md)
find .opencode/knowledge -name '*.md'   # knowledge files
find .templates -name '*.template'   # artifact templates
find docs/research -name '*.md'          # research source notes (cited by knowledge files)
```

## File Naming Conventions

### Artifact Names in Flow Attrs

Artifact names in `in` and `out` lists use these conventions:

| Pattern | Meaning | Example |
|---------|---------|---------|
| `filename.md` | A specific document | `domain_model.md`, `product_definition.md` |
| `dir/<param>.ext` | A specific instance identified by parameter | `features/<feature_name>.feature`, `interview-notes/<session>.md`, `adr/<slug>.md` |
| `dir/*.ext` | Multiple documents of that type available in `in` | `interview-notes/*.md`, `adr/*.md` |
| `conceptual_name` | A runtime artifact that passes between states within a flow | `typed_source_stubs`, `test_implementations` |

**Wildcards (`*`)** in `in` indicate that multiple documents of that type are available. List the directory contents first, then read selectively based on the task. When a state creates a single instance, use a `<parameter>` name instead.

**Runtime artifacts** (not backed by files) use descriptive names that make their purpose clear: `typed_source_stubs` (source files with type signatures only), `test_skeletons` (test files with structure only), `test_implementations` (tests with bodies), `source_implementations` (production code with behavior), `refactored_source` (code after refactoring pass), `feature_commits` (git commits for one feature), `merged_commits` (commits merged to local main), `root_cause_analysis` (analysis findings).

**Environment artifacts** are produced by tooling rather than flow states: `coverage_reports` (test coverage output), `test_output` (test runner output), `linter_output` (linter output). These exist on disk after running the relevant tool and are referenced in `in` but not in any state's `out`.

## Flowr Commands

All commands require the virtual environment: `source .venv/bin/activate`

| Command | Purpose |
|---------|---------|
| `python -m flowr validate <flow>.yaml` | Validate a flow definition |
| `python -m flowr validate` (no arg) | Validate all flows |
| `python -m flowr states <flow>.yaml` | List all states in a flow |
| `python -m flowr next <flow>.yaml <state>` | Show valid transitions from a state |
| `python -m flowr transition <flow>.yaml <state> <trigger>` | Compute next state given a trigger |
| `python -m flowr transition <flow>.yaml <state> <trigger> --evidence key=value` | Compute next state with condition evidence |
| `python -m flowr check <flow>.yaml <state> [target]` | Check condition guards for a state |
| `python -m flowr mermaid <flow>.yaml` | Export flow as Mermaid diagram |
| `./scripts/flowr-utils.sh validate [flow]` | Validate flow(s) via wrapper script |
| `./scripts/flowr-utils.sh view <flow>` | View flow as Mermaid diagram |
| `./scripts/flowr-utils.sh list` | List all available flows |
| `./scripts/flowr-utils.sh graph` | Generate interactive D3.js visualization |

## Project Commands

Check `pyproject.toml` for taskipy tasks and tool configuration. Common commands:

| Command | Purpose |
|---------|---------|
| `task test` | Run tests with short tracebacks |
| `task test-fast` | Run fast tests only (excludes slow marker) |
| `task test-coverage` | Run tests with coverage report |
| `task test-build` | Run full test suite with coverage, hypothesis stats, and HTML report |
| `task run` | Run the application |

Linting and formatting:

| Command | Purpose |
|---------|---------|
| `ruff check .` | Lint check |
| `ruff format .` | Auto-format |
| `ruff check --fix .` | Auto-fix lint issues |

## Session Protocol
1. `flowr status` → current state, owner, skills, transitions
2. Announce the state (one line), then load the skill and do the work
3. `flowr advance <transition>` to move to next state

### Within a State

Announce the state once at the top, then go quiet:

- **State entry:** One line stating where you are — e.g. `→ specify-feature`. No preamble, no recap of how you got there.
- **Dispatch to the owner agent:** The state's `owner` field names the responsible agent. Call that agent as a subagent with the state's `skills` loaded, passing the state attrs as context. Owner mapping: `PO` → product-owner, `DE` → domain-expert, `SE` → software-engineer, `SA` → system-architect, `R` → reviewer, `Design Agent` → design-agent, `Setup Agent` → setup-agent.
- **Respect the artifact contract:** The state's attrs define what the owner agent may read and write:
  - `in`: Read-only context. List what's available first, then read only what the task requires. No section specifications.
  - `out`: May create or edit. Section sub-lists indicate which sections the state should produce or update.
  - Files not in `out` must not be written to. If findings affect an artifact outside the output contract, flag them in output notes and defer the change to the step that owns that artifact.
  - The flow contract must always be followed unless the stakeholder explicitly asks to break it.
  - **Artifact existence guarantee:** When a flow state needs a file artifact that does not yet exist, it is created from the matching template in `.templates/` (if one exists). If no template exists for a non-Python file referenced in `in`/`out`, raise an error for the stakeholder to decide. Files are then updated when a state writes to them or their sections. Environment artifacts (e.g., `coverage_reports`, `test_output`, `linter_output`) are produced by tooling rather than flow states — they exist on disk after running the relevant tool and are referenced in `in` but not in any state's `out`.
- **Read inputs on demand, not eagerly.** When `in` lists artifacts, discover what's available first (`ls`, `find`), then read only the files and sections needed for the current task. The `in` list defines what you *may* read, not what you *must* read up front. This applies to all files — spec documents, production code, and test code. List directories first, read selectively.
- **Specification documents are read-only during development.** During TDD and review cycles, the SE and reviewer may ONLY modify production code and test code. Spec document inconsistencies must be FLAGGED in output notes, not fixed directly. Spec docs are owned by other flow states and can only be changed through the appropriate flow step — after code is reviewed and approved.
- **Do the work with the fewest, quietest commands.** Suppress verbose output. If a command can be scoped with a flag, pipe, or limit — use it. Don't dump full files or directory listings when a targeted query answers the question.
- **No narration between steps.** The command and its output are the conversation. Don't echo what you're about to do or what you just did.
- **State exit:** `flowr advance` and the transition name. Nothing more.