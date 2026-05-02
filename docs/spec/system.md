# System Overview: smith

> Current-state description of the production system.
> Updated by the Software Architect when domain understanding changes (rare).
> Contains only completed features — nothing from backlog or in-progress.
> This document captures what code cannot express: WHY contexts exist, HOW they relate, WHAT the aggregate boundaries are and why.

---

## Summary

smith is a CLI tool that clones standardised agent configurations (AGENTS.md, .opencode/, .flowr/, .templates/) to any project directory — and purges cleanly when done. It resolves template sources from GitHub repos, HTTP URLs, or local directories, filters files through an allowed-topics safety boundary, and tracks written files in a managed .gitignore section for clean removal. The system is delivered as a pip-installable package (`agents-smith`) with one external runtime dependency (`requests`, for downloading GitHub archives and URL templates). Its sole bounded context is **Connection Management**: clone and purge.

---

## Delivery

**Mechanism:** CLI (command-line interface)

The `smith` command is the sole delivery mechanism. Users interact with two subcommands: `clone` and `purge`. The CLI is a thin adapter that parses arguments and delegates to core functions. The domain logic has no knowledge of argparse or terminal output — core functions produce domain results, and the CLI layer translates these into human-readable output and exit codes.

---

## Context (C4 Level 1)

### Actors

| Actor | Description |
|-------|-------------|
| Software Engineer | Runs `smith clone` in any project directory to immediately start working with standard AI agent workflows; runs `smith purge` when done |
| Tech Lead | Standardises AI agent configurations across the team's projects by cloning the same template to each one |

### Systems

| System | Kind | Description |
|--------|------|-------------|
| smith | Internal | CLI tool that manages the Connection lifecycle: clone and purge |
| Template Source | External | Provides agentic files for provisioning. Three variants: GitHub repo (zip archive), local path (filesystem), remote URL (HTTP/HTTPS zip/tar.gz) |
| Project Directory | External | The target project directory where agentic files are written/removed |

### Interactions

| Interaction | Behaviour | Technology |
|-------------|-----------|------------|
| Engineer → smith | Runs CLI commands (clone, purge) | Shell / terminal |
| smith → Template Source (GitHub) | Downloads repository archive (zip) | requests (HTTPS) |
| smith → Template Source (URL) | Downloads zip/tar.gz archive | requests (HTTPS) |
| smith → Template Source (Local) | Walks directory tree | os.walk / pathlib |
| smith → Project Directory | Writes/removes agentic files; manages .gitignore section | pathlib, shutil |

---

## Container (C4 Level 2)

### Boundary: smith

| Container | Technology | Responsibility |
|-----------|------------|----------------|
| CLI Layer | argparse (stdlib) | Parse CLI arguments, dispatch to core functions, format output, set exit codes |
| Core Functions | Python (pure) | Source resolution, file fetching, allowed-topics filtering, clone/purge orchestration |
| Gitignore Manager | Python (pure) | Read and mutate the smith-managed section of .gitignore |

### Interactions

| Interaction | Behaviour |
|-------------|-----------|
| CLI → Core Functions | Parses CLI args, calls clone/purge with resolved source |
| Core → Gitignore Manager | After writing files, delegates .gitignore section management |
| Core → Template Source | Fetches template files: requests for GitHub/URL, pathlib/os for local |
| Core → Project Directory | Writes fetched files, skips existing unless --overwrite |

---

## Module Structure

| Module | Responsibility | Bounded Context |
|--------|----------------|-----------------|
| `smith.cli` | CLI argument parsing and command dispatch | Connection Management |
| `smith.core` | Source resolution, file fetching (GitHub, URL, local), allowed-topics filtering, clone/purge orchestration | Connection Management |
| `smith.gitignore` | .gitignore section management (add, read, replace) | Connection Management |

---

## Domain Model Documentation

### Why Each Context Exists

| Bounded Context | Business Capability | Why It's Separate |
|-----------------|---------------------|-------------------|
| Connection Management | Fetching template files into a project and tracking/removing them | This is the sole bounded context — smith has a single, focused purpose and does not need multiple contexts |

### Aggregate Boundary Rationale

| Aggregate | Why These Entities Are Grouped | Transactional Invariant |
|-----------|-------------------------------|------------------------|
| Connection | File specs, .gitignore section, and source resolution are grouped because clone must write files and update .gitignore together, and purge must read .gitignore to know what to remove | All smith-managed files must be listed in the .gitignore section for purge to work correctly |

---

## Active Constraints

- **Allowed-topics safety boundary:** Only files matching `ALLOWED_TOPICS` (AGENTS.md, .opencode/, .flowr/, .templates/) are ever written during clone — no other files from the template source can reach the project directory
- **Overwrite protection:** Existing directories and files are skipped by default; `--overwrite` is required to replace them
- **Clean .gitignore tracking:** The managed section uses start/end markers (`# smith managed` / `# end smith managed`) for idempotent management; purge only removes files listed in this section
- **Archive prefix stripping:** When archives contain a single top-level directory (e.g., `temple8-main/`), it is stripped so files are written at project root
- **Source resolution chain:** CLI `--source` arg > `[tool.smith] source` in pyproject.toml > default (`github:nullhack/temple8`)
- **Minimal runtime dependencies:** Only `requests` beyond Python stdlib; argparse, tomllib, pathlib, shutil, zipfile, tarfile, dataclasses all come from stdlib

---

## Key Decisions

- **argparse as CLI framework** — Sufficient for two subcommands; maintains minimal runtime dependencies. See `docs/adr/ADR_20260502_cli-argparse.md`.
- **Flat module structure (not hexagonal)** — YAGNI: with two commands and no persistent state, the complexity of a hexagonal architecture is not justified. Core logic lives in `smith/core.py`, gitignore management in `smith/gitignore.py`, CLI in `smith/cli.py`. The module boundary is the natural seam for future extraction.
- **Allowed-topics filter as safety boundary** — Only files matching the `ALLOWED_TOPICS` tuple are ever written, regardless of what the template source contains. This prevents template sources from writing arbitrary files to the project directory. See `docs/adr/ADR_20260502_allowed-topics-as-safety-boundary.md`.
- **Direct file writes (no atomic staging)** — Current implementation writes files directly without temp-directory staging. This is a deliberate simplicity trade-off for the current scope (two commands, no concurrent access). If atomicity becomes a requirement, a staging layer can be added without changing the core API.
- **Stateless .gitignore section (no metadata file)** — Connection state is tracked via the `# smith managed` / `# end smith managed` section in .gitignore. No separate `.smith.yaml` or metadata file is created. This keeps smith stateless and reversible.
- **No smart merge** — For directories that already exist, `--overwrite` replaces entirely. No partial merge logic. This is a deliberate simplicity trade-off (YAGNI > DRY). See `docs/adr/ADR_20260502_overwrite-protection.md`.

---

## ADRs

See `docs/adr/` for the full decision record.

---

## Completed Features

See `docs/features/` for accepted features.

---

## Changes

| Date | Source | Change | Reason |
|------|--------|--------|--------|
| 2026-05-02 | initial | System overview derived from working code | Baseline from existing implementation on rebuild/minimal-v2 branch |