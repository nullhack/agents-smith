# PM_20260501_missing-overwrite-flag: --overwrite CLI flag not implemented despite Must-priority BDD examples

## Failed At

Development — TDD cycle (green phase). The `--overwrite` flag was present in the interview notes, feature spec, domain model, and technical design, but never implemented in `cli.py` or `Connection.connect()`.

## Root Cause

The `--overwrite` flag was specified at **every planning stage** but dropped during implementation:

1. **Interview notes** (IN_20260501_smith-commands-specification.md): Q6 "Destructive overwrites without explicit `--overwrite` flag" listed as a failure mode. Q10 explicitly describes `--overwrite` behavior. Q13 confirms "refuse to overwrite unless `--overwrite` is passed."

2. **Feature spec** (smith-commands.feature): Two Must-priority examples reference it — `@id:2a5f83d0` and `@id:7d22e1d6`, both using `smith connect --overwrite`.

3. **Domain model** (domain_model.md line 23): `ConnectionRequested` event includes `[--overwrite]` in the command signature.

4. **Technical design** (technical_design.md lines 93, 101, 617, 624, 650): `--overwrite` is documented as a CLI flag, a configuration key, and part of the safety invariant.

5. **Implementation**: **Missing entirely.** `cli.py` has no `--overwrite` argument. `Connection.connect()` has no `overwrite` parameter. `Connection._resolve_specs()` has the domain logic for skipping user-tracked files, but the flag to bypass it was never wired through.

The failure occurred at the **TDD green phase** — when writing the minimum production code to make failing tests pass, the `--overwrite` flag was never added because no test exercised the CLI handler with the `--overwrite` argument. All tests for examples `2a5f83d0` and `7d22e1d6` tested the domain logic (`Connection._resolve_specs`) through in-memory stubs, which validated the skip/overwrite behavior in isolation but never verified the CLI-to-domain wiring.

## Missed Gate

**Structure review** — the review verified test coverage and BDD example pass rate, but did not trace each `@id` example from CLI invocation through to domain behavior. The gate checked "does a test function exist for each `@id`" but not "does each `@id` that references a CLI flag actually test that the flag reaches the domain layer."

Additionally, the **definition-of-done** gate (if it was applied) should have verified that the technical design spec's CLI interface section matches the actual `cli.py` argument parser. The spec lists `smith connect [--from <source>] [--overwrite]` but the parser only has `--from`.

## Stage-by-Stage Trace

| Stage | `--overwrite` Present? | Gap |
|-------|----------------------|-----|
| Interview (IN_20260501) | Yes — Q6, Q10, Q13, QA2 | None |
| Feature spec (smith-commands.feature) | Yes — `@id:2a5f83d0`, `@id:7d22e1d6` | None |
| Domain model | Yes — `ConnectionRequested` event | None |
| Technical design | Yes — CLI interface, config keys, safety invariant | None |
| TDD green phase | **No** — `cli.py` and `Connection.connect()` never received the flag | **Dropped here** |
| Structure review | Not checked — no CLI-to-domain traceability gate | **Missed here** |

## Fix

1. Add `--overwrite` argument to the `connect_parser` in `cli.py`
2. Wire `--overwrite` through `handle_connect` to `Connection.connect()`
3. Update `Connection.connect()` to accept an `overwrite` parameter that bypasses the skip-user-tracked-files logic
4. Write CLI-level integration tests for `smith connect --overwrite`
5. Add a review gate that verifies every `@id` example in the feature spec traces to a CLI handler test (not just a domain-layer test)
6. Add a definition-of-done check that compares the technical design's CLI interface section against the actual argument parser

## Restart Check

- Verify `smith connect --overwrite` works end-to-end from CLI through domain layer
- Verify BDD examples `2a5f83d0` and `7d22e1d6` pass as CLI integration tests
- Verify `smith status` suggests `--overwrite` in the partial connection message
- Run `task lint && task static-check && task test` and confirm 0 errors