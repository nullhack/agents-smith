# ADR_20260502_flat-module-structure

## Status

Accepted

## Context

Smith has two commands (clone, purge), no persistent state, no server component, and no async requirements. The codebase needs a module structure that is simple, navigable, and appropriate for the current scope. The main branch uses hexagonal architecture (domain/application/infrastructure layers), but the current rebuild (minimal-v2) intentionally reduces scope.

## Interview

| Question | Answer |
|---|---|
| How many commands does smith currently support? | Two: clone and purge |
| Is hexagonal architecture needed for two commands? | No — YAGNI. The complexity doesn't justify the abstraction |
| What is the natural seam for future extraction? | The module boundary (cli.py, core.py, gitignore.py) |

## Decision

Use a flat module structure with three modules: `cli.py` (delivery), `core.py` (domain logic), `gitignore.py` (.gitignore management). No separate domain/application/infrastructure layers.

## Reason

With two commands and no persistent state, a hexagonal architecture is over-engineering. The flat module structure keeps the codebase simple and navigable. `core.py` contains all domain logic (source resolution, fetching, allowed-topics filtering, clone/purge). `gitignore.py` encapsulates .gitignore section management. `cli.py` is a thin delivery layer. The module boundary is the natural seam for future extraction if complexity grows.

## Alternatives Considered

- **Hexagonal architecture (Ports & Adapters)**: Main branch uses this pattern with domain/application/infrastructure layers and Protocol-based ports. Appropriate for four commands with atomic writes, status, and update — but not justified for two commands with direct file writes.
- **Layered architecture**: Similar overhead to hexagonal without the testability benefit at this scope.

## Consequences

- (+) Simple, navigable codebase — three modules, clear responsibilities
- (+) Easy to understand for new contributors
- (+) Natural extraction points if complexity grows (core.py can be split)
- (-) If commands grow to 4+ with complex invariants, the flat structure may need refactoring
- (-) No Protocol-based ports means testing requires mocking at the function level rather than the adapter level

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Accepted? |
|------|------------|--------|------------|-----------|
| Commands grow beyond flat structure ergonomics | Medium | Low | Refactor into hexagonal when scope justifies it (update, status commands) | Yes |
| Testing requires filesystem access | Low | Low | GitignoreManager can be tested with temp directories; core logic can be tested with mock requests | Yes |