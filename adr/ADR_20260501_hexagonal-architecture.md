# ADR_20260501_hexagonal-architecture

## Status

Accepted

## Context

smith's domain logic enforces four critical invariants (atomicity, safety, clean separation, consistency) that must not be coupled to infrastructure details like filesystem operations, network access, or CLI argument parsing. The quality attributes rank Safety, Atomicity, and Clean Separation above Usability — the domain invariants are the core value, and the delivery mechanism (CLI) is a thin adapter. The project also needs to support multiple template source types (bundled, local path, remote URL) without changing domain logic.

Forces:
- Safety, Atomicity, and Clean Separation are Must-quality attributes that must be enforced in the domain layer
- Multiple template source types (bundled, local path, URL) require different infrastructure implementations
- Zero runtime dependency constraint means no framework can provide dependency injection
- Testability is a Should-quality attribute — domain logic must be testable without filesystem or network access
- The domain is small and cohesive (single bounded context, single aggregate)

## Interview

| Question | Answer |
|---|---|
| Which architectural style should smith use? | Hexagonal (Ports & Adapters) |

## Decision

Use Hexagonal Architecture (Ports & Adapters) with four layers: domain, application, infrastructure, delivery. Domain defines Protocol interfaces (ports); infrastructure implements them as adapters. The dependency arrow always points inward.

## Reason

Hexagonal architecture keeps the domain invariant enforcement independent of filesystem, network, and CLI concerns. The four quality attributes (Safety, Atomicity, Clean Separation, Consistency) are all enforced in the pure domain layer — no filesystem or network imports in domain code. Template source variations are handled by infrastructure adapters implementing a TemplateSourcePort interface, satisfying Modifiability without domain changes.

## Alternatives Considered

- **Layered architecture (traditional 3-tier):** Would work but doesn't enforce the strict dependency inversion needed. Domain could accidentally import infrastructure through shared layers. Rejected because it doesn't make the port/adapter boundary explicit.
- **Microservices architecture:** Over-engineered for a single-bounded-context CLI tool. Rejected because there's no inter-service communication need.
- **Event-driven architecture:** No asynchronous processing or event sourcing requirements. Rejected because smith's commands are synchronous request-response.

## Consequences

- (+) Domain invariants are testable in isolation via port mocks — no filesystem or network in unit tests
- (+) New template source types added as infrastructure adapters without domain changes
- (+) CLI is a thin delivery adapter — can be replaced without touching domain logic
- (-) More files and indirection than a simple script — mitigated by the domain being small (single aggregate)
- (-) Protocol interfaces must be maintained alongside implementations — mitigated by keeping ports minimal (4 ports)

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Accepted? |
|------|------------|--------|------------|-----------|
| Over-engineering for a small CLI tool | Medium | Low | Domain is a single aggregate; the overhead is 4 port interfaces and 6 adapter classes — proportional to the problem | Yes |
| Port interfaces drift from actual needs | Low | Medium | Write tests against ports first (TDD); ports evolve with domain needs | Yes |