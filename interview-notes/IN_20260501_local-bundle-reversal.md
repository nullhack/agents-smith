# IN_20260501_local-bundle-reversal — Revert GitHub-based bundled resolution to local bundle

> **Status:** COMPLETE
> **Interviewer:** PO
> **Participant(s):** Stakeholder
> **Session type:** Scope refinement

---

## General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | Why revert from GitHub-based download to local bundle? | GitHub-based resolution adds runtime network dependency, cache staleness risk, and implementation complexity that outweighs the freshness benefit for the default template source |
| Q2 | What should BundledTemplateSource do instead? | Read agentic files from `smith/data/` package directory via `importlib.resources` — no network calls, no caching, no external dependency for the default source |
| Q3 | What files go in `smith/data/`? | Agentic files only: AGENTS.md, .opencode/, .templates/, .flowr/ — derived from the agents-smith v8_release branch |
| Q4 | How is `smith/data/` kept in sync with agents-smith? | Manual script (`scripts/update-bundle.sh`) that downloads the agents-smith v8_release archive and copies agentic files to `smith/data/` |
| Q5 | Should `requests` still be a dependency? | Yes — UrlTemplateSource needs it for tar.gz/zip downloads. But bundled source has no runtime network dependency |
| Q6 | Should URL sources use caching? | No — URL sources re-download every time. No persistent cache for any source type |
| Q7 | What about BDD examples a1b2c3d4 (network failure) and e5f6g7h8 (cache fallback)? | Deprecate both — bundled source no longer needs network access. Add new Should examples for URL source download failure |
| Q8 | Should `TemplateSource.kind` still include "bundled"? | Yes — `kind="bundled"` stays. `smith connect` without `--from` defaults to `bundled:agents-smith` |
| Q9 | Should the `TemplateSourceAdapter` fallback be removed? | Yes — the adapter should just dispatch on `source.kind` with no fallback. Use cases pass the source directly |

## Feature: smith-commands

| ID | Question | Answer |
|----|----------|--------|
| Q10 | What happens on URL source download failure? | `smith connect --from <url>` exits with code 1 and an error message. No fallback to bundled source — the user explicitly chose a URL source |
| Q11 | What archive formats should UrlTemplateSource support? | `.tar.gz` and `.zip` — the two formats GitHub provides for branch/tag archives |
| Q12 | Should the agentic file filter apply to URL sources? | Yes — `_is_agentic_path()` filter applies to all URL sources. Only AGENTS.md, .opencode/, .templates/, .flowr/ are written |

---

## Quality Attributes

| ID | Attribute | Scenario | Target | Priority |
|----|-----------|----------|--------|----------|
| QA1 | Simplicity | When `smith connect` runs without `--from`, no network call is made | 0 network calls for bundled source | Must |
| QA2 | Reliability | When `smith connect --from <url>` fails to download, exit code 1 with clear error | < 1 second to report failure | Must |
| QA3 | Maintainability | When agents-smith v8_release updates, a single script updates `smith/data/` | 1 command to update bundled files | Must |

---

## Pain Points Identified

- GitHub-based resolution introduced runtime network dependency for the default use case
- Cache staleness was discovered during end-to-end testing (stale cache had only 2 files)
- GitHub download + cache logic was more complex than local bundle

## Business Goals Identified

- `smith connect` with no arguments should "just work" — no network required
- Template freshness is maintained by the update script, not runtime downloads

## Terms to Define (for glossary)

- Local Bundle (update Bundled Template Resolution entry)

## Action Items

- [x] Revert BundledTemplateSource to `importlib.resources`-based local bundle
- [x] Implement UrlTemplateSource (tar.gz/zip via requests, agentic filter, no cache)
- [x] Remove TemplateSourceAdapter fallback parameter
- [x] Deprecate BDD examples a1b2c3d4 and e5f6g7h8
- [x] Add new URL source failure examples
- [x] Create ADR-007 superseding ADR-006
- [x] Update spec documents