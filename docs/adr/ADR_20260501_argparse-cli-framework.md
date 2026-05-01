# ADR_20260501_argparse-cli-framework

## Status

Accepted

## Context

smith needs a CLI framework to support four subcommands (`connect`, `disconnect`, `update`, `status`) with options (`--from <path/url>`, `--overwrite`). The project has a hard constraint of zero runtime dependencies. The current codebase already uses argparse (stdlib) for `--help` and `--version`. The CLI framework choice is architecturally significant because it constrains the entire command dispatch structure and is hard to change later without rewriting all command handlers.

**Feature:** smith-commands (all four CLI commands)

Forces:
- Zero runtime dependency constraint from `product_definition.md` and `system.md`
- Four subcommands with options — argparse supports subparsers natively
- The quality attribute ranking places Usability below Safety, Atomicity, and Clean Separation — a simpler CLI is acceptable if it meets the four-command requirement
- The delivery mechanism is CLI-only — no HTTP, no TUI, no GUI

## Interview

| Question | Answer |
|---|---|
| Which CLI framework should smith use? | argparse (stdlib) |

## Decision

Use argparse as the CLI framework for all four subcommands.

## Reason

argparse is part of the Python stdlib, satisfies the zero-runtime-dependency constraint, and supports subparsers for multi-command CLIs. The four subcommands are well within argparse's capability — no complex nested commands, no shell completion, no rich terminal output required.

## Alternatives Considered

- **Click**: Mature, excellent for complex CLIs, but introduces a runtime dependency (`click`). Rejected because it violates the zero-dependency constraint.
- **Typer**: Built on Click with type annotations, but also introduces a runtime dependency (`typer` + `click`). Rejected for the same reason.
- **Docopt**: Declarative CLI from docstrings, but introduces a runtime dependency and has weaker subparser support. Rejected.
- **Cleo**: Full-featured CLI framework used by Poetry, but introduces a runtime dependency and is over-engineered for four commands. Rejected.

## Consequences

- (+) Zero runtime dependencies maintained — `pip install agents-smith` works with no additional packages
- (+) Consistent with existing codebase (`__main__.py` already uses argparse)
- (+) Stdlib guarantee — argparse will always be available on any Python 3.13 installation
- (-) argparse subparser API is more verbose than Click/Typer — more boilerplate per command
- (-) No built-in shell completion, rich formatting, or progress bars — mitigated by keeping CLI output simple (text + exit codes)
- (-) Switching to Click/Typer later would require rewriting all command handlers — mitigated by hexagonal architecture (command handlers are thin adapters; domain logic is independent)

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Accepted? |
|------|------------|--------|------------|-----------|
| argparse subparser ergonomics lead to verbose command dispatch code | Medium | Low | Keep command handlers thin (dispatch to application use cases) | Yes |
| Future CLI complexity exceeds argparse capability | Low | Medium | Hexagonal architecture isolates CLI framework — can swap without domain changes | Yes |
| argparse `required` subparser behavior differs across Python versions | Low | Low | Python 3.13 is the only target version | Yes |