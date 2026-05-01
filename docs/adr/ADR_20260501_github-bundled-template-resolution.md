# ADR_20260501_github-bundled-template-resolution

## Status

Superseded by ADR-007 (local bundled template resolution)

## Context

The `BundledTemplateSource` currently resolves template files from `smith/data/` — a directory of 85 hardcoded copies of the project's own `.opencode/`, `.flowr/`, `.templates/`, and `AGENTS.md` files. This approach has several problems:

1. **Staleness:** The bundled files are copies that must be manually updated. They will drift from the actual agents-smith templates over time.
2. **Coupling:** Every template update requires a new smith package release, even though smith is the consumer, not the owner, of these templates.
3. **Size:** 85 files add unnecessary bulk to the package distribution.
4. **Wrong ownership:** The agents-smith repository (specifically its `v8_release` branch) is the authoritative source for these files, not the smith package.

The agents-smith PyPI package (v7.2.20260423) only contains `app/__init__.py` and `app/__main__.py` — it does not expose template data as package resources, so `importlib.resources` cannot be used to read templates from a agents-smith package.

Forces:
- Templates should always be current without requiring a new smith release
- The default template source must work reliably (network or cache)
- Network failure should not prevent `smith connect` if the cache is populated
- The solution should be simple and maintainable

## Interview

| Question | Answer |
|---|---|
| Should we use stdlib `urllib.request` or `requests` for HTTP? | Use `requests` — cleaner API, better error handling, worth the dependency |
| Should downloaded templates be cached locally? | Yes — cache in `~/.cache/smith/` to avoid re-downloading on every connect/update |
| Should the default GitHub branch/tag be configurable? | No — default to `v8_release` for now; will change in future but not configurable today |
| Should `smith/data/` be removed? | Yes — delete the entire directory; it contains stale copies |

## Decision

Resolve the bundled `agents-smith` template source by downloading the GitHub archive at runtime from `https://github.com/nullhack/agents-smith/archive/refs/heads/v8_release.tar.gz`, extracting it, and caching the files locally in `~/.cache/smith/agents-smith/`. Delete `smith/data/` entirely. Add `requests` as the only external runtime dependency.

## Reason

GitHub-based resolution ensures templates are always current without requiring a new smith package release. Local caching avoids redundant network requests. The `requests` library provides significantly better HTTP handling than `urllib.request` for this use case. Removing `smith/data/` eliminates stale copies and the maintenance burden of keeping them in sync.

## Alternatives Considered

- **importlib.resources with packaged templates (status quo):** Templates in `smith/data/` will go stale and require manual updates. The agents-smith PyPI package does not expose template data as resources. Rejected because of staleness and coupling.
- **urllib.request for HTTP downloads:** The stdlib HTTP client lacks connection pooling, timeout defaults, and clean error handling that `requests` provides. Rejected because the API is harder to use correctly and test.
- **Git submodule for agents-smith:** Adds complexity to the build process and still requires packaging template files. Rejected because it doesn't solve the staleness problem.
- **No caching (re-download every time):** Wasteful network requests on every `smith connect`/`smith update`. Rejected because of performance and usability impact on repeated commands.

## Consequences

- (+) Templates are always current — no need for a new smith release when templates change
- (+) `smith/data/` is removed — no stale copies, smaller package distribution
- (+) Local cache enables offline use after first download
- (-) `requests` is added as a runtime dependency — breaks the previous "zero runtime dependencies" constraint; mitigated by `requests` being the only external dependency
- (-) First `smith connect` requires network access — mitigated by clear error message on failure and cache fallback for subsequent use
- (-) Cache directory management adds implementation complexity — mitigated by using standard OS cache directories (`~/.cache/smith/`)

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Accepted? |
|------|------------|--------|------------|-----------|
| GitHub is unavailable on first `smith connect` | Low | Medium | Clear error message with exit code 1; suggest retrying or using `--from <local-path>` | Yes |
| Cache corruption | Low | Low | Delete cache directory and re-download; smith does not rely on cache integrity for safety | Yes |
| `v8_release` branch is renamed or deleted | Low | High | Default URL is a module-level constant that can be updated in a patch release; future enhancement could make it configurable | Yes |
| `requests` security vulnerability | Low | Medium | Pin minimum version in pyproject.toml; dependabot alerts for known CVEs | Yes |