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

## Allowed Topics

**Definition:** A set of path prefixes (AGENTS.md, .opencode/, .flowr/, .templates/) that determine which files from a template source are eligible for writing during a clone operation.

**Aliases:** none

**Example:** Only files matching allowed topics are extracted from the archive; a README.md in the archive is skipped.

**Source:** smith-clone-purge

---

## Agentic File

**Definition:** A file or directory that smith manages in a cloned project, drawn from a template source and written to the project directory.

**Aliases:** managed file, smith file

**Example:** AGENTS.md, .opencode/, .templates/, and .flowr/ are the agentic files that `smith clone` writes to a project directory.

**Source:** smith-clone-purge

---

## Clone

**Definition:** The CLI command `smith clone [--source <path/url>] [--overwrite]` that fetches template files from a source, filters them by allowed topics, writes them to the project directory, and adds a managed .gitignore section.

**Aliases:** clone command, smith clone

**Example:** Running `smith clone` in a project directory writes AGENTS.md, .opencode/, .templates/, and .flowr/ and adds their patterns to .gitignore under `# smith managed`.

**Source:** smith-clone-purge

---

## Purge

**Definition:** The CLI command `smith purge` that reads the smith-managed .gitignore section and deletes every file and directory listed there, leaving the section itself intact.

**Aliases:** purge command, smith purge

**Example:** Running `smith purge` removes AGENTS.md, .opencode/, .flowr/, .templates/ if they are listed in the managed section.

**Source:** smith-clone-purge

---

## FileSpec

**Definition:** A value object representing a single file to be written during a clone operation, with a relative path and binary content.

**Aliases:** file specification

**Example:** A FileSpec with relative_path=".opencode/agents/default.md" and content=bytes carries the agent configuration file from the template source.

**Source:** smith-clone-purge

---

## GitignoreManager

**Definition:** A component that reads and mutates the smith-managed section of a project's .gitignore file, using start (`# smith managed`) and end (`# end smith managed`) markers to delimit the section.

**Aliases:** gitignore manager, managed section manager

**Example:** After clone writes files, the GitignoreManager adds a `# smith managed` section listing the top-level patterns.

**Source:** smith-clone-purge

---

## Managed .gitignore Section

**Definition:** A delimited section in .gitignore marked with `# smith managed` and `# end smith managed` that contains entries for all agentic file patterns, added on clone and preserved on purge.

**Aliases:** gitignore section, managed section

**Example:** After `smith clone`, .gitignore contains a `# smith managed` section with entries like `.opencode/`, `.flowr/`, and `AGENTS.md`.

**Source:** smith-clone-purge

---

## Overwrite

**Definition:** A boolean flag (`--overwrite`) that, when set, allows clone to replace existing files and directories; when unset (default), clone skips any directory or file that already exists.

**Aliases:** none

**Example:** Running `smith clone --overwrite` replaces an existing AGENTS.md with the one from the template source.

**Source:** smith-clone-purge

---

## Smith

**Definition:** A CLI tool that clones standardised agent configurations (AGENTS.md, .opencode/, .flowr/, .templates/) to any project directory, enabling engineers to immediately work with consistent AI agent workflows — and purges cleanly when done.

**Aliases:** agents-smith (PyPI package name), smith (Python module name)

**Example:** `smith clone` in any project directory sets up AGENTS.md, .opencode/, .templates/, and .flowr/ so engineers can start using AI-assisted workflows immediately.

**Source:** smith-clone-purge

---

## Source

**Definition:** A template location that smith fetches files from, expressed as a GitHub shorthand (`github:user/repo`), an HTTP/HTTPS URL to a zip or tar.gz archive, or a local directory path.

**Aliases:** template source

**Example:** `github:nullhack/temple8` is the default source; others include `https://example.com/templates.zip` or `/path/to/local/template`.

**Source:** smith-clone-purge

---

## Source Resolution

**Definition:** The process of determining which template source to use, following a priority chain: CLI `--source` argument > `tool.smith.source` in pyproject.toml > default source (`github:nullhack/temple8`).

**Aliases:** none

**Example:** When `smith clone` is run without `--source` in a project with `[tool.smith] source = "github:org/repo"` in pyproject.toml, the source resolves to `github:org/repo`.

**Source:** smith-clone-purge

---

## Top-Level Patterns

**Definition:** The set of top-level directory names (with trailing slash) and file names derived from written file specs, which are added to the smith-managed .gitignore section.

**Aliases:** none

**Example:** Given specs with paths .opencode/agents/default.md and AGENTS.md, the top-level patterns are [".opencode/", "AGENTS.md"].

**Source:** smith-clone-purge