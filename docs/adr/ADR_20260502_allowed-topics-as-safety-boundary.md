# ADR_20260502_allowed-topics-as-safety-boundary

## Status

Accepted

## Context

Smith fetches archives from external sources (GitHub repos, URLs, local directories) that may contain arbitrary files. Writing all files from an untrusted source into a project is dangerous — it could overwrite source code, configs, or inject malicious files. Smith needs a hard boundary on what files it will ever write.

## Interview

| Question | Answer |
|---|---|
| Should users be able to configure which file paths are allowed? | No — the allowed topics are a safety boundary, not a configuration point |
| What topics should be allowed? | AGENTS.md, .opencode/, .flowr/, .templates/ — the four standard agentic config locations |

## Decision

Use a compile-time constant ALLOWED_TOPICS tuple containing ("AGENTS.md", ".opencode/", ".flowr/", ".templates/") as the hard filter. No file outside these prefixes is ever written, regardless of source.

## Reason

A fixed allowlist is the simplest and safest boundary. Making it configurable would shift security responsibility to the user and increase the attack surface — a misconfigured allowlist could allow writing arbitrary files.

## Alternatives Considered

- **Configurable allowlist in pyproject.toml**: More flexible but shifts security responsibility to users and increases risk of misconfiguration
- **Blocklist instead of allowlist**: Impossible to enumerate all dangerous paths; allowlist is the correct security posture

## Consequences

- (+) Strong safety guarantee — only agentic config files are ever written
- (+) Simple to reason about and test
- (-) Users cannot add new topic categories without modifying the source code
- (-) If a new agentic config directory is introduced, it requires a code change

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Accepted? |
|------|------------|--------|------------|-----------|
| New agentic config directories are introduced | Medium | Low | ALLOWED_TOPICS is a single tuple constant — easy to update in a new release | Yes |