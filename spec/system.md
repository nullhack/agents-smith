# System Overview: smith

> Current-state description of the production system.
> Updated by the Software Architect when domain understanding changes (rare).
> Contains only completed features — nothing from backlog or in-progress.
> This document captures what code cannot express: WHY contexts exist, HOW they relate, WHAT the aggregate boundaries are and why.

---

## Summary

smith is an AI pair programming platform that connects standardised agent configurations (AGENTS.md, .opencode/, .templates/, .flowr/) to any project directory — and disconnects cleanly when done. Its sole bounded context is the **Connection lifecycle**: connect, disconnect, update, and status. The system is delivered as a CLI tool (`smith`) with one external runtime dependency (`requests`, for URL template sources), using hexagonal architecture to keep domain logic independent of filesystem operations and template resolution. The primary users are software engineers and tech leads who need consistent AI agent configurations across projects.

---

## Delivery

**Mechanism:** CLI (command-line interface)

The `smith` command is the sole delivery mechanism. Users interact with four subcommands: `connect`, `disconnect`, `update`, `status`. The CLI is a thin adapter that parses arguments and delegates to application use cases. The domain has no knowledge of argparse or terminal output — it enforces invariants and produces domain objects; the delivery layer translates these into human-readable output and exit codes.

---

## Context (C4 Level 1)

### Actors

| Actor | Description |
|-------|-------------|
| Software Engineer | Runs `smith connect` in any project directory to immediately start working with standard AI agent workflows; runs `smith disconnect` when done |
| Tech Lead | Standardises AI agent configurations across the team's projects by connecting the same template to each one |

### Systems

| System | Kind | Description |
|--------|------|-------------|
| smith | Internal | CLI tool that manages the Connection lifecycle: connect, disconnect, update, status |
| Template Source | External | Provides agentic files for provisioning. Three variants: bundled (agents-smith, packaged in smith/data/), local path (filesystem), remote URL (HTTP/HTTPS) |
| Project Directory | External | The target project directory where agentic files are written/removed |

### Interactions

| Interaction | Behaviour | Technology |
|-------------|-----------|------------|
| Engineer → smith | Runs CLI commands (connect, disconnect, update, status) | Shell / terminal |
| smith → Template Source | Reads template files for provisioning | importlib.resources (bundled), requests (URL), pathlib (local) |
| smith → Project Directory | Writes/removes agentic files atomically; manages .gitignore section with source metadata in header; stateless — no metadata file | pathlib, shutil, tempfile |

---

## Container (C4 Level 2)

### Boundary: smith

| Container | Technology | Responsibility |
|-----------|------------|----------------|
| CLI Delivery Layer | argparse (stdlib) | Parse CLI arguments, dispatch to use cases, format output, set exit codes |
| Application Services | Python (pure) | Orchestrate use cases: connect, disconnect, update, status. Enforce invariants via domain layer |
| Domain Layer | Python (pure) | Enforce invariants (atomicity, safety, clean separation, consistency). Define ports (Protocols) that infrastructure must implement |
| Infrastructure Adapters | Python + requests | Implement domain ports: BundledTemplateSource (importlib.resources from smith/data), LocalTemplateSource, UrlTemplateSource (requests + tarfile/zipfile), AtomicFileSystem, GitignoreManager, SectionMetadata |

### Interactions

| Interaction | Behaviour |
|-------------|-----------|
| CLI → Application Services | Dispatches parsed CLI arguments to the appropriate use case (ConnectUseCase, DisconnectUseCase, etc.) |
| Application Services → Domain | Delegates invariant enforcement to the Connection aggregate; uses ports for side effects |
| Infrastructure → Domain | Implements domain port Protocols; dependency arrow points inward (infrastructure depends on domain, not vice versa) |
| Infrastructure → Template Source | Reads template files: importlib.resources from packaged data (bundled), filesystem read (local), HTTP download (URL) |
| Infrastructure → Project Directory | Writes/removes agentic files atomically via temp-directory staging; manages .gitignore section with source metadata; stateless — no metadata file |

---

## Module Structure

| Module | Responsibility | Bounded Context |
|--------|----------------|-----------------|
| `smith.domain.connection` | Connection aggregate root — enforces atomicity, safety, clean separation, consistency invariants | Connection |
| `smith.domain.value_objects` | TemplateSource, GitignoreSection, ConnectionStatus, FileSpec — immutable value objects | Connection |
| `smith.domain.ports` | TemplateSourcePort, FileSystemPort, GitignorePort, MetadataPort — Protocol interfaces defining what the domain needs | Connection |
| `smith.application.connect` | ConnectUseCase — orchestrates conflict check, template resolution, atomic write, .gitignore update, metadata save | Connection |
| `smith.application.disconnect` | DisconnectUseCase — orchestrates file removal, preserving the .gitignore section as a guard | Connection |
| `smith.application.update` | UpdateUseCase — orchestrates connection check, template resolution, atomic overwrite, .gitignore update, metadata update | Connection |
| `smith.application.status` | StatusUseCase — orchestrates connection check, file presence check, status report | Connection |
| `smith.infrastructure.template_source` | BundledTemplateSource (importlib.resources from smith/data/), LocalTemplateSource, UrlTemplateSource (requests + tarfile/zipfile, no cache) — implement TemplateSourcePort | Connection |
| `smith.infrastructure.filesystem` | AtomicFileSystem — implements FileSystemPort with temp-directory staging | Connection |
| `smith.infrastructure.gitignore` | GitignoreManager — implements GitignorePort with delimited section management | Connection |
| `smith.infrastructure.metadata` | SectionMetadata — delegates to GitignoreManager for source metadata in gitignore section header (stateless — no .smith.yaml file) | Connection |
| `smith.delivery.cli` | build_parser(), main(), command handlers — argparse setup and dispatch | Connection |

---

## Domain Model Documentation

### Why Each Context Exists

| Bounded Context | Business Capability | Why It's Separate |
|-----------------|---------------------|-------------------|
| Connection | Manage the full lifecycle of connecting agentic files to a project directory | The Connection lifecycle is the core domain — connect, disconnect, update, status. It encapsulates all invariants (atomicity, safety, clean separation, consistency) and is the sole entry point for all four commands. No other context is needed because the domain is small and cohesive. |

### Aggregate Boundary Rationale

| Aggregate | Why These Entities Are Grouped | Transactional Invariant |
|-----------|-------------------------------|------------------------|
| Connection | The Connection aggregate root owns the TemplateSource, GitignoreSection, and the list of FileSpecs. All operations (connect, disconnect, update, status) go through the Connection root. The file set cannot exist independently — it is always part of a Connection. | **Atomicity:** either all agentic files are written or none are. **Safety:** user-tracked files are skipped; smith-managed files are auto-updated. **Clean separation:** on disconnect, no agentic files remain. **Consistency:** .gitignore section and agentic file set are always in sync. |

---

## Active Constraints

- **Minimal runtime dependencies:** The package has one external runtime dependency (`requests`), used only for URL template source resolution. The bundled `agents-smith` source reads from packaged files via `importlib.resources` — no network call required. All other functionality uses Python stdlib. See ADR-007.
- **Atomicity via temp-directory staging:** All file writes must be staged to a temporary directory before being committed to the project directory. No partial connections are allowed.
- **Safety via pre-write conflict check:** Before any write, the project directory must be scanned for existing agentic files. User-tracked files are skipped; smith-managed files are auto-updated.
- **Clean separation via managed .gitignore section:** The `# smith managed` / `# end smith managed` delimiters must be used to mark the section. On disconnect, agentic files are removed but the section is preserved as a guard for future usage.
- **Hexagonal architecture:** Domain logic must not import from infrastructure, application, or delivery layers. The dependency arrow always points inward.
- **Usability:** `smith connect` must complete (files written and .gitignore updated) in under 1 minute in any project directory.

---

## Key Decisions

- **argparse as CLI framework** — Sufficient for four subcommands; maintains minimal runtime dependencies. See ADR-001.
- **Atomic file writes via temp-directory staging** — All files written to a temp directory first, then moved atomically. On failure, the temp directory is discarded. See ADR-002.
- **Hexagonal architecture (Ports & Adapters)** — Domain logic is independent of filesystem, network, and CLI. Ports are Protocol interfaces defined in the domain layer; infrastructure adapters implement them.
- **Stateless design — no .smith.yaml** — Connection state is inferred from the `# smith managed` section in `.gitignore`. Source metadata is stored in the section header (e.g., `# smith managed source:agents-smith`). No separate metadata file is created. ADR-004 (originally defining .smith.yaml) is superseded by this stateless decision.
- **No smart merge** — For `.flowr/` and `.templates/` that already exist, `--overwrite` replaces entirely. No partial merge logic. This is a deliberate simplicity trade-off (YAGNI > DRY).
- **Local bundled template resolution** — The default `agents-smith` template source reads agentic files from `smith/data/` via `importlib.resources`. No network call is required. A manual script (`scripts/update-bundle.sh`) syncs the bundle from the agents-smith `v8_release` branch when a new release is prepared. See ADR-007.

---

## ADRs

See `docs/adr/` for the full decision record.

- ADR-001: Use argparse as CLI framework (minimal runtime dependencies) — `docs/adr/ADR_20260501_argparse-cli-framework.md`
- ADR-002: Atomic file writes via temp-directory staging — `docs/adr/ADR_20260501_atomic-file-writes-via-temp-directory.md`
- ADR-003: Hexagonal architecture (Ports & Adapters) — `docs/adr/ADR_20260501_hexagonal-architecture.md`
- ADR-004: .smith.yaml metadata file — `docs/adr/ADR_20260501_smith-yaml-metadata.md`
- ADR-005: No smart merge for .flowr/ and .templates/ — `docs/adr/ADR_20260501_no-smart-merge.md`
- ADR-006: GitHub-based bundled template resolution — **Superseded** by ADR-007
- ADR-007: Local bundled template resolution (importlib.resources) — `docs/adr/ADR_20260501_local-bundled-template-resolution.md`

---

## Completed Features

See `docs/features/` for accepted features.

---

## Changes

| Date | Source | Change | Reason |
|------|--------|--------|--------|
| 2026-05-01 | architecture-assessment | Initial system overview | New feature: smith-commands (connect, disconnect, update, status) |
| 2026-05-01 | IN_20260501_agents-smith-dependency-resolution | Changed bundled template resolution from importlib.resources/smith/data/ to GitHub-based download + local cache; updated dependency constraint from zero runtime deps to one (requests) | Bundled template files in smith/data/ were stale copies that would go out of sync; GitHub-based resolution ensures templates are always current |
| 2026-05-01 | IN_20260501_local-bundle-reversal | Reverted bundled template resolution to local package (importlib.resources + smith/data/); fully implemented UrlTemplateSource; removed caching; deprecated BDD examples a1b2c3d4 and e5f6g7h8; superseded ADR-006 with ADR-007 | GitHub-based resolution introduced runtime network dependency and cache staleness issues; local bundle provides instant offline default |