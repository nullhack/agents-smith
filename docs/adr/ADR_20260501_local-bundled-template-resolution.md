# ADR_20260501_local-bundled-template-resolution

## Status

Accepted — supersedes ADR-006 (GitHub-based bundled template resolution)

## Context

ADR-006 replaced the local `smith/data/` bundle with GitHub-based runtime download + local cache. This introduced problems discovered during end-to-end testing:

1. **Runtime network dependency:** `smith connect` without `--from` requires network access on first run, violating the principle that the default source should "just work"
2. **Cache staleness:** A stale cache directory with incomplete content was served instead of re-downloading, producing incorrect results
3. **Complexity:** Download, extraction, caching, and cache invalidation logic added significant implementation overhead for the default use case
4. **Wrong default behavior:** The default template source should be the most reliable path, not one that depends on external infrastructure

The agents-smith v8_release branch is the source of truth for agentic files, but smith should carry a local copy as part of its distribution rather than downloading at runtime.

Forces:
- The default `smith connect` experience should be instant and offline-capable
- Template freshness is a release-time concern, not a runtime concern
- `requests` is still needed for UrlTemplateSource (non-default source types)
- The `smith/data/` directory must be kept in sync with agents-smith v8_release via a manual script

## Interview

| Question | Answer |
|---|---|
| Should bundled templates be packaged locally or downloaded at runtime? | Packaged locally — `smith connect` without `--from` must work offline |
| Should `requests` still be a dependency? | Yes — UrlTemplateSource needs it for tar.gz/zip downloads |
| How is `smith/data/` kept in sync with agents-smith? | Manual script (`scripts/update-bundle.sh`) that downloads and copies agentic files |
| Should URL sources cache downloads? | No — re-download every time; no persistent cache for any source type |
| What about the deprecated BDD examples a1b2c3d4 and e5f6g7h8? | Deprecate — they test network failure and cache fallback for bundled source, which no longer applies |

## Decision

Package agentic files in `smith/data/` and resolve them at runtime via `importlib.resources`. BundledTemplateSource reads from the package directory — no network calls, no caching. UrlTemplateSource (fully implemented) downloads tar.gz/zip archives via `requests`, extracts to a temp directory, applies the agentic filter, and returns FileSpec objects — no persistent cache. Delete the GitHub download and caching code from BundledTemplateSource. Add `scripts/update-bundle.sh` for manual sync from agents-smith v8_release.

## Reason

Local packaging ensures `smith connect` works offline and instantly for the default case. Runtime download complexity is unnecessary for the default source. Template freshness is maintained through release-time updates, not runtime downloads.

## Alternatives Considered

- **GitHub-based download + local cache (ADR-006, superseded):** Adds runtime network dependency, cache staleness risk, and implementation complexity. Rejected because the default experience should be instant and offline.
- **No `requests` dependency at all:** Would prevent UrlTemplateSource from working. Rejected because URL source support is a required feature.
- **Git submodule for agents-smith:** Adds build complexity and still requires packaging files. Rejected because it doesn't simplify the distribution.
- **Persistent cache for URL sources:** Adds cache invalidation complexity with minimal benefit since URL sources are used infrequently. Rejected for simplicity.

## Consequences

- (+) `smith connect` without `--from` works instantly and offline
- (+) No cache staleness or invalidation issues for the default source
- (+) Simpler implementation — no download, extraction, or caching for BundledTemplateSource
- (+) `requests` dependency is only used for UrlTemplateSource, not the default path
- (-) `smith/data/` must be kept in sync with agents-smith v8_release via manual script
- (-) Template updates require a new smith release (same as pre-ADR-006 behavior)
- (-) `smith/data/` adds ~85 files to the package distribution

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Accepted? |
|------|------------|--------|------------|-----------|
| `smith/data/` drifts from agents-smith v8_release | Medium | Low | `scripts/update-bundle.sh` syncs agentic files; CI could automate this in future | Yes |
| Package size increases by ~85 files | Low | Low | Agentic files are small text files; total size is negligible | Yes |
| UrlTemplateSource download fails | Medium | Medium | Clear error message with exit code 1; user can retry or use `--from <local-path>` | Yes |
| `importlib.resources` path resolution differs across Python versions | Low | Low | Use `importlib.resources.files()` which is stable in Python 3.9+ | Yes |