# Glossary: smith

> Living glossary of domain terms used in this project.
> Written and maintained by the Domain Expert during Discovery.
> Append-only: never edit or remove past entries. If a term changes, mark it retired in favor of the new entry and write a new entry.
> Code and tests take precedence over this glossary — if they diverge, refactor the code, not this file.

---

## Entry Format

```
## <Term>

**Definition:** <one sentence — genus + differentia: "A [category] that [distinguishes it from others in that category]">

**Aliases:** <deprecated synonyms the team should stop using, or "none">

**Example:** <one sentence showing the term in use in this project; optional but encouraged>

**Source:** <feature stem or discovery session date>
```

Entries are sorted alphabetically.

---

## Agentic File

**Definition:** A file or directory that smith manages in a connected project, drawn from a template source and written to the project directory.

**Aliases:** managed file, smith file

**Example:** AGENTS.md, .opencode/, .templates/, and .flowr/ are the agentic files that `smith connect` writes to a project directory.

**Source:** smith-commands

---

## Agentic File Set

**Definition:** The complete set of agentic files (AGENTS.md, .opencode/, .templates/, .flowr/) that smith writes as a unit during connection. In code, represented as `list[FileSpec]` rather than a separate entity.

**Aliases:** file set, managed set

**Example:** The Agentic File Set is written atomically — either all four items are present or none are.

**Source:** smith-commands

---

## Atomic Connection

**Definition:** A connection guarantee that either all agentic files are written to the project directory or none are, ensuring no partial state exists.

**Aliases:** none

**Example:** When `smith connect` encounters a write failure, it rolls back all previously written files to maintain an atomic connection.

**Source:** smith-commands

---

## Clean Separation

**Definition:** A disconnection guarantee that no agentic files remain in the project directory after `smith disconnect`, leaving only .gitignore entries as a trace.

**Aliases:** none

**Example:** After running `smith disconnect`, the project directory contains no .opencode/ directory, no .templates/ directory, no .flowr/ directory, and no AGENTS.md file.

**Source:** smith-commands

---

## Connect

**Definition:** The CLI command `smith connect [--from <source>] [--overwrite]` that writes all agentic files from a template source to the current project directory, adds a managed .gitignore section, and establishes a connection.

**Aliases:** connect command, smith connect

**Example:** Running `smith connect` in a project directory writes AGENTS.md, .opencode/, .templates/, and .flowr/ and adds their patterns to .gitignore under `# smith managed`.

**Source:** smith-commands

---

## Connection

**Definition:** The aggregate root representing the state of a project directory's relationship to smith's agentic configuration, tracking whether the project is connected, the template source, and the set of managed files.

**Aliases:** none

**Example:** A Connection is established by `smith connect` and removed by `smith disconnect`.

**Source:** smith-commands

---

## Disconnect

**Definition:** The CLI command `smith disconnect` that removes all agentic files managed by smith from the current project directory while preserving the `# smith managed` section in .gitignore as a guard for future usage.

**Aliases:** disconnect command, smith disconnect

**Example:** Running `smith disconnect` removes AGENTS.md, .opencode/, .templates/, .flowr/ (only those tracked in the `# smith managed` section), but preserves the section header in .gitignore.

**Source:** smith-commands

---

## Managed .gitignore Section

**Definition:** A delimited section in .gitignore marked with `# smith managed` that contains entries for all agentic file patterns, added on connect and preserved on disconnect. The section's presence indicates an existing or previous connection.

**Aliases:** gitignore section, managed section, GitignoreSection (code)

**Example:** After `smith connect`, .gitignore contains a `# smith managed` section with entries like `.opencode/` and `.flowr/sessions/`.

**Source:** smith-commands

---

## Safety

**Definition:** A connection guarantee that user-tracked files (not managed by smith) are never overwritten; smith-managed files are auto-updated, ensuring zero silent overwrites.

**Aliases:** overwrite protection

**Example:** When `smith connect` finds an existing AGENTS.md that is user-tracked (not in `# smith managed`), it skips user-tracked files and proceeds with the remaining files.

**Source:** smith-commands

---

## Smith

**Definition:** An AI pair programming platform that connects standardised agent configurations to any project directory, enabling engineers to immediately work with consistent AI agent workflows.

**Aliases:** agents-smith (PyPI package name), smith (Python module name)

**Example:** `smith connect` in any project directory sets up AGENTS.md, .opencode/, .templates/, and .flowr/ so engineers can start using AI-assisted workflows immediately.

**Source:** smith-commands

---

## Status

**Definition:** The CLI command `smith status` that reports whether the current project directory is connected, which agentic files are present, and which template source was used.

**Aliases:** status command, smith status

**Example:** Running `smith status` in a connected project shows "Connected" with a list of present agentic files and the template source.

**Source:** smith-commands

---

## Template Source

**Definition:** The origin of agentic files to be written during connection: the default agents-smith templates, a local directory path, or a remote URL specified via `--from`.

**Aliases:** source, template source

**Example:** `smith connect --from ./my-templates` uses a local directory as the template source instead of the default agents-smith templates.

**Source:** smith-commands

---

## Update

**Definition:** The CLI command `smith update` that refreshes agentic files in a connected project directory from the original template source, applying any changes from the source to the project.

**Aliases:** update command, smith update

**Example:** Running `smith update` after the default agents-smith templates have been updated writes the latest versions of agentic files to the project directory.

**Source:** smith-commands

---

## ConnectionStatus

**Definition:** A value object representing the current state of a project directory's connection to smith's agentic configuration: connected, disconnected, or partial (some but not all agentic files present).

**Aliases:** status, connection state

**Example:** Running `smith status` returns a ConnectionStatus of "connected" when all agentic files are present, or "partial" when some are missing.

**Source:** smith-commands

---

## FileSpec

**Definition:** A value object representing a single file or directory to be written during a connect or update operation, with a source path (from the template) and a destination path (in the project directory).

**Aliases:** file specification, agentic file (informal)

**Example:** A FileSpec for AGENTS.md has source `templates/AGENTS.md` and destination `./AGENTS.md` in the project directory.

**Source:** smith-commands

---

## Managed Section Header (smith metadata)

**Definition:** Source metadata stored within the `# smith managed` section header of `.gitignore`, using the format `# smith managed source:<location>`. Connection state is inferred from the presence of the managed section — no separate metadata file is created (stateless design).

**Aliases:** section header metadata, stateless metadata

**Example:** After `smith connect --from ./my-templates`, the `.gitignore` section header reads `# smith managed source:./my-templates`.

**Source:** smith-commands

---

## Agents-Smith

**Definition:** The default bundled template source for smith, providing the standard agentic files (AGENTS.md, .opencode/, .templates/, .flowr/) packaged in the `smith/data/` directory and read via `importlib.resources`.

**Aliases:** agents-smith, default template, bundled template

**Example:** Running `smith connect` without `--from` reads the agents-smith templates from the packaged `smith/data/` directory — no network call required.

**Source:** smith-commands, IN_20260501_local-bundle-reversal

---

## Bundled Template Resolution

**Definition:** The process by which the default `agents-smith` template source reads template files from the `smith/data/` package directory via `importlib.resources`, rather than downloading them at runtime.

**Aliases:** local bundle resolution, packaged template resolution

**Example:** When an engineer runs `smith connect`, BundledTemplateSource reads agentic files from `smith/data/AGENTS.md`, `smith/data/.opencode/`, etc. via `importlib.resources` — no network access or caching required.

**Source:** IN_20260501_local-bundle-reversal

---

## Retired Terms

| Term | Retired In Favor Of | Reason | Date |
|------|---------------------|--------|------|
| Cache Directory | — | Bundled source no longer uses caching; URL sources re-download each time | 2026-05-01 |
| GitHub-based Resolution | Local Bundle Resolution | Bundled source now reads from packaged files, not GitHub downloads | 2026-05-01 |
| CLI Application | Connection | Product scope changed from project template to AI pair programming platform; the CLI is now one delivery mechanism for the Connection aggregate | 2026-05-01 |
| CLI Entrypoint | Connection | Product scope changed; the entry point is now the `smith` command, not a generic CLI application | 2026-05-01 |
| Package Metadata | TemplateSource | Package metadata is an infrastructure concern; the domain concept is the template source that provides files | 2026-05-01 |
| Project Template | smith | Product scope changed from project template to AI pair programming platform | 2026-05-01 |
| Quality Gate | (kept, but not a domain term) | Quality Gate is a process concept, not a smith domain term | 2026-05-01 |
| Workflow Engine | (removed) | The workflow engine concept belongs to agents-smith (the template source), not to smith's domain | 2026-05-01 |