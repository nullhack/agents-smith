# Domain Model: smith

> Current understanding of the business domain.
> Updated by the Domain Expert when domain understanding evolves.
> This document captures what code cannot express: WHY entities exist, HOW aggregates are bounded, and WHAT business capabilities each context serves.
>
> **Evolving document:** Event Storming fills the Event Map, Aggregate Candidates, and Context Candidates sections (workshop draft). Domain Modeling then formalizes them into Entities, Relationships, and Aggregate Boundaries.

---

## Summary

smith is an AI pair programming platform that connects standardised agent configurations (AGENTS.md, .opencode/, .templates/, .flowr/) to any project directory — and disconnects cleanly when done. Its domain is centred on the **Connection lifecycle**: connect, disconnect, update, and status. The domain has one bounded context — the **Connection context** — which owns the Connection aggregate and supporting value objects. The initial delivery (smith-commands) validates the full connect/work/disconnect cycle end-to-end with four CLI commands.

---

## Event Map

### Domain Events

| Event | Description | Trigger | Bounded Context |
|-------|-------------|---------|-----------------|
| `ConnectionRequested` | User invoked `smith connect` in a project directory | User runs `smith connect [--from <source>] [--overwrite]` | Connection |
| `ConnectionEstablished` | All agentic files written to the project directory atomically | All files written successfully | Connection |

| `ConnectionRolledBack` | Partial write detected; all written files removed to restore clean state | Write failure during connect | Connection |
| `DisconnectionRequested` | User invoked `smith disconnect` in a connected project directory | User runs `smith disconnect` | Connection |
| `DisconnectionCompleted` | All agentic files removed; managed .gitignore section preserved | All files removed successfully | Connection |
| `UpdateRequested` | User invoked `smith update` in a connected project directory | User runs `smith update` | Connection |
| `UpdateCompleted` | Agentic files updated to latest from template source | All files updated successfully | Connection |
| `StatusRequested` | User invoked `smith status` in a project directory | User runs `smith status` | Connection |
| `StatusReported` | Connection status displayed to the user | Status check completed | Connection |

### Commands

| Command | Description | Produces Event | Actor |
|---------|-------------|----------------|-------|
| `Connect` | Write all agentic files to a project directory from a template source | `ConnectionEstablished` or `ConnectionRolledBack` | Engineer |
| `Disconnect` | Remove all agentic files and managed .gitignore entries from a project directory | `DisconnectionCompleted` | Engineer |
| `Update` | Refresh agentic files from the template source in an already-connected project | `UpdateCompleted` | Engineer |
| `ReportStatus` | Display whether the project directory is connected and which agentic files are present | `StatusReported` | Engineer |

### Read Models

| Read Model | Description | Consumes Event | Used By |
|------------|-------------|----------------|---------|
| `ConnectionStatus` | Whether the project is connected, which files are present, and the template source | `StatusRequested` | CLI output |
| `RollbackLog` | Files that were written before rollback was triggered | `ConnectionRolledBack` | CLI error output |

---

## Context Candidates

> Filled during Event Storming. Formalized in Bounded Contexts section below by Domain Modeling.

| Candidate | Responsibility | Grouped Aggregates | Notes |
|-----------|---------------|--------------------|-------|
| Connection | Owns the full lifecycle of connecting/disconnecting agentic files to a project directory | Connection | Single context — the Connection lifecycle is the domain |

---

## Aggregate Candidates

> Filled during Event Storming. Formalized in Aggregate Boundaries section below by Domain Modeling.

| Candidate | Events Grouped | Tentative Root Entity | Notes |
|-----------|---------------|-----------------------|-------|
| Connection | `ConnectionRequested`, `ConnectionEstablished`, `ConnectionRolledBack`, `DisconnectionRequested`, `DisconnectionCompleted`, `UpdateRequested`, `UpdateCompleted`, `StatusRequested`, `StatusReported` | Connection | Single aggregate — the Connection is the sole entry point for all four commands |

---

## Bounded Contexts

| Context | Responsibility | Key Entities | Integration Points |
|---------|----------------|--------------|-------------------|
| Connection | Manage the full lifecycle of connecting agentic files to a project directory: connect, disconnect, update, and status | Connection, TemplateSource, GitignoreSection | Template Source (external dependency for file resolution) |

> smith has one bounded context (Connection). The Template Source is an infrastructure dependency, not a separate bounded context — it provides files but has no independent domain logic or invariants. If template versioning or validation becomes a domain concern in future, it may be extracted into its own context.

---

## Entities

| Name | Type | Description | Bounded Context | Aggregate Root? |
|------|------|-------------|-----------------|-----------------|
| Connection | Entity | The aggregate root representing a project directory's connection to smith's agentic configuration. Tracks connection state, template source, and the set of managed files. | Connection | Yes |

---

## Value Objects

| Name | Type | Description | Bounded Context |
|------|------|-------------|-----------------|
| TemplateSource | Where agentic files come from: default (agents-smith), local path, or URL. Immutable once resolved. | Connection |
| GitignoreSection | The `# smith managed` section in .gitignore. Contains entries for all agentic file patterns. Managed as a unit — added on connect, removed on disconnect. | Connection |
| ConnectionStatus | The current state of a project's connection: connected, disconnected, or partial (some but not all agentic files present). | Connection |
| FileSpec | A single file or directory to be written during connect or update, with a source path (from the template) and a destination path (in the project directory). | Connection |

---

## Relationships

| Subject | Relation | Object | Cardinality | Notes |
|---------|----------|--------|-------------|-------|
| Connection | resolves | TemplateSource | 1:1 | Each connection resolves one template source |
| Connection | maintains | GitignoreSection | 1:1 | Each connection manages one .gitignore section |
| Connection | manages | FileSpec | 1:many | Each connection manages multiple file specifications |

---

## Aggregate Boundaries

| Aggregate | Root Entity | Invariants | Bounded Context |
|-----------|-------------|------------|-----------------|
| Connection | Connection | **Atomicity:** either all agentic files are written or none are — no partial connections, ever. **Safety:** user-tracked files (not managed by smith) are never overwritten; smith-managed files are auto-updated — zero silent overwrites of user-tracked files, ever. **Clean separation:** on disconnect, no agentic files remain (only .gitignore entries) — zero orphaned files after disconnect. **Consistency:** the .gitignore section and the agentic file set must always be in sync — connected means files present AND .gitignore section present; disconnected means no agentic files present but the .gitignore section is preserved as a guard. | Connection |

---

## Changes

| Date | Source | Change | Reason |
|------|--------|--------|--------|
| 2026-05-01 | architecture-assessment | Complete rewrite for corrected product scope | Previous domain model described the wrong product (Python project template). smith is an AI pair programming platform with connect/disconnect/update/status commands. |