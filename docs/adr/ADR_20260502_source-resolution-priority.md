# ADR_20260502_source-resolution-priority

## Status

Accepted

## Context

Smith needs to know where to fetch templates from. The source can be specified in three ways: a CLI flag, a config key in pyproject.toml, or the built-in default. The resolution order must be clear and predictable.

## Interview

| Question | Answer |
|---|---|
| Which takes precedence: CLI flag or config file? | CLI flag — explicit user intent should always win |
| What should happen if pyproject.toml exists but has no [tool.smith] section? | Fall through to default — missing config is not an error |

## Decision

Source resolution follows a strict priority chain: CLI --source flag > [tool.smith] source in pyproject.toml > default (github:nullhack/temple8).

## Reason

This follows the standard 12-factor app convention of command-line flags overriding configuration files, which override defaults. It gives users three levels of control without complexity.

## Alternatives Considered

- **Environment variable as middle layer**: Adds complexity for marginal benefit; pyproject.toml already serves as project-level config
- **Config file only (no default)**: Forces every project to configure a source; the default provides zero-config usage

## Consequences

- (+) Predictable and follows established conventions
- (+) Zero-config usage works via the default
- (-) The default source (temple8) is a specific GitHub repo — changes to that repo affect all users who don't configure a source

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Accepted? |
|------|------------|--------|------------|-----------|
| Default repo becomes unavailable | Low | Medium | Users can configure their own source in pyproject.toml | Yes |