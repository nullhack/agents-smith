# ADR_20260502_cli-argparse

## Status

Accepted

## Context

Smith needs a command-line interface with at least two subcommands (clone, purge) and optional flags (--source, --overwrite). The CLI framework should be minimal, sufficient, and not add runtime dependencies.

## Interview

| Question | Answer |
|---|---|
| How many subcommands are needed? | Two for now (clone, purge); may grow to four (update, status) |
| Is interactive input needed? | No — smith runs in scripts and CI; all input is via flags |

## Decision

Use argparse from the Python standard library as the CLI framework.

## Reason

Argparse is sufficient for two subcommands with options, is part of the standard library (no external dependency), and provides --help and --version automatically. With the current scope, there is no justification for a more complex CLI framework.

## Alternatives Considered

- **Click**: More ergonomic for complex CLIs but adds an external dependency for no functional benefit at this scope
- **Typer**: Nice type annotations but adds both typer and click as dependencies

## Consequences

- (+) Zero additional runtime dependencies
- (+) Built-in --help and --version support
- (+) Standard Python — every developer knows argparse
- (-) Verbose for complex subcommand trees (acceptable at current scope)

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Accepted? |
|------|------------|--------|------------|-----------|
| CLI grows beyond argparse ergonomics | Low | Low | Migrate to Click/Typer when scope justifies it | Yes |