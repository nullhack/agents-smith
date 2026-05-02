# Domain Model: smith

> Current understanding of the business domain.
> Updated by the Domain Expert when domain understanding evolves.
> This document captures what code cannot express: WHY entities exist, HOW aggregates are bounded, and WHAT business capabilities each context serves.
>
> **Evolving document:** Derived from working code as baseline.

---

## Summary

smith manages the lifecycle of AI agent configuration files in a project. The domain centers on two operations: clone (fetch template files from a source, filter by allowed topics, write them into a project, and track them in .gitignore) and purge (read the .gitignore section and remove only the listed files). The core invariants are: only allowed-topic files are ever written, purge removes only tracked files, and existing files are skipped unless `--overwrite` is passed.

---

## Event Map

### Domain Events

| Event | Description | Trigger | Bounded Context |
|-------|-------------|---------|-----------------|
| `SourceResolved` | The template source has been determined from CLI arg, config, or default | Source resolution completes | Connection Management |
| `FilesFetched` | Template files have been fetched from a source and filtered by allowed topics | Archive extraction or local walk completes | Connection Management |
| `FilesCloned` | Template files have been written to the project directory and tracked in .gitignore | `clone` command completes | Connection Management |
| `GitignoreSectionUpdated` | The smith-managed section in .gitignore has been created or replaced | Clone writes files | Connection Management |
| `FilesPurged` | Smith-managed files and directories have been removed from the project | `purge` command completes | Connection Management |

### Commands

| Command | Description | Produces Event | Actor |
|---------|-------------|----------------|-------|
| `clone` | Fetch template files from a source, filter, write to project, update .gitignore | `SourceResolved` → `FilesFetched` → `FilesCloned` → `GitignoreSectionUpdated` | Engineer |
| `purge` | Read .gitignore section and remove all smith-managed files | `FilesPurged` | Engineer |

### Read Models

| Read Model | Description | Consumes Event | Used By |
|------------|-------------|----------------|---------|
| `.gitignore section` | The smith-managed section listing which top-level files/dirs are tracked | `GitignoreSectionUpdated` | `purge` command |
| `written file specs` | The list of FileSpecs actually written (after filtering) | `FilesCloned` | .gitignore section update |

---

## Context Candidates

> Filled during Event Storming. Formalized in Bounded Contexts section below by Domain Modeling.

| Candidate | Responsibility | Grouped Aggregates | Notes |
|-----------|---------------|--------------------|-------|
| Connection Management | Owning the full lifecycle of cloning/purging template files | Connection | Single context — smith has one cohesive purpose |

---

## Aggregate Candidates

> Filled during Event Storming. Formalized in Aggregate Boundaries section below by Domain Modeling.

| Candidate | Events Grouped | Tentative Root Entity | Notes |
|-----------|---------------|-----------------------|-------|
| Connection | `SourceResolved`, `FilesFetched`, `FilesCloned`, `GitignoreSectionUpdated`, `FilesPurged` | clone/purge functions | All events are part of one atomic clone/purge operation |

---

## Bounded Contexts

| Context | Responsibility | Key Entities | Integration Points |
|---------|----------------|--------------|-------------------|
| Connection Management | Fetch, filter, write, and remove template files; manage .gitignore tracking | FileSpec, GitignoreManager | Reads from GitHub/URL/local sources; writes to project filesystem and .gitignore |

---

## Entities

| Name | Type | Description | Bounded Context | Aggregate Root? |
|------|------|-------------|-----------------|-----------------|
| FileSpec | Value Object | A relative path and binary content pair representing a single file to write | Connection Management | No |
| GitignoreManager | Entity | Manages reading and mutating the smith-managed section in .gitignore | Connection Management | No |
| Connection | Aggregate | Orchestrates the full clone or purge operation: source resolution, file fetching, filtering, writing, and .gitignore tracking | Connection Management | Yes |

---

## Value Objects

| Name | Type | Description | Bounded Context |
|------|------|-------------|-----------------|
| Source | str | The template source string: a GitHub shorthand (`github:user/repo`), URL, or local path | Connection Management |
| Allowed Topics | tuple[str, ...] | The set of path prefixes that gate which files are written during clone | Connection Management |

---

## Relationships

| Subject | Relation | Object | Cardinality | Notes |
|---------|----------|--------|-------------|-------|
| Connection | has many | FileSpec | 1:N | A clone operation produces multiple file specs |
| Connection | uses | GitignoreManager | 1:1 | Each clone/purge uses one gitignore manager |
| FileSpec | derived from | Source | N:1 | Multiple file specs come from one source |

---

## Aggregate Boundaries

| Aggregate | Root Entity | Invariants | Bounded Context |
|-----------|-------------|------------|-----------------|
| Connection | clone/purge functions | **Reliability:** only files matching ALLOWED_TOPICS prefixes are written — zero disallowed files, ever. **Reversibility:** purge removes only files listed in the managed .gitignore section — zero non-managed files deleted. **Safety:** existing directories and files are skipped unless --overwrite is passed. | Connection Management |

---

## Changes

| Date | Source | Change | Reason |
|------|--------|--------|--------|
| 2026-05-02 | initial | Domain model derived from working code | Baseline from existing implementation on rebuild/minimal-v2 branch |