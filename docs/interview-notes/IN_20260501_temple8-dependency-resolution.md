# Interview Notes: Agents-Smith Dependency Resolution

> **Status:** COMPLETE
> **Interviewer:** SA
> **Participant(s):** nullhack
> **Session type:** Scope refinement

---

## General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | How should the bundled template source resolve template files? | Download from the agents-smith GitHub repository's `v8_release` branch at runtime, not from packaged local files |
| Q2 | Should we use stdlib `urllib.request` or `requests` for HTTP? | Use `requests` — cleaner API, better error handling, worth the dependency |
| Q3 | Should downloaded templates be cached locally? | Yes — cache in `~/.cache/smith/` to avoid re-downloading on every connect/update |
| Q4 | Should the default GitHub branch/tag be configurable? | No — default to `v8_release` for now; will change in future but not configurable today |
| Q5 | Should `smith/data/` (85 stale bundled files) be removed? | Yes — delete the entire `smith/data/` directory; it contains stale copies of the project's own agentic files |

## Architecture: Bundled Template Source

| ID | Question | Answer |
|----|----------|--------|
| Q6 | How should BundledTemplateSource download the archive? | Download `https://github.com/nullhack/agents-smith/archive/refs/heads/v8_release.tar.gz` as a tarball via GitHub's archive API |
| Q7 | How should the archive be extracted and resolved into FileSpec objects? | Extract to a temp directory, walk the extracted directory, and collect files matching the agentic file set (AGENTS.md, .opencode/, .templates/, .flowr/) |
| Q8 | What should happen on network failure? | Exit with code 1 and a clear error message indicating the bundled template source could not be downloaded |
| Q9 | What is the cache structure? | `~/.cache/smith/agents-smith/` — store the extracted template files; on subsequent resolves, check if cached files exist and are fresh enough before re-downloading |
| Q10 | What is the cache invalidation strategy? | Re-download when the cache is empty or on explicit `smith update`; future enhancement could add ETag/Last-Modified checking |

## Dependency Change

| ID | Question | Answer |
|----|----------|--------|
| Q11 | What dependency does this add? | `requests` — the only runtime dependency beyond stdlib |
| Q12 | Does this change the "zero runtime dependencies" constraint? | Yes — the constraint changes from "zero runtime dependencies" to "one runtime dependency (requests)" |

---

## Quality Attributes

| ID | Attribute | Scenario | Target | Priority |
|----|-----------|----------|--------|----------|
| QA1 | Usability | When an engineer runs `smith connect` without network, they get a clear error message | Error message within 1 second | Must |
| QA2 | Performance | When cache is warm, `smith connect` resolves templates from local cache | < 100ms for cached resolution | Should |
| QA3 | Reliability | When GitHub is temporarily unavailable, `smith update` fails gracefully with exit code 1 | No partial state on failure | Must |

---

## Pain Points Identified

- `smith/data/` contains 85 stale copies of the project's own `.opencode/`, `.flowr/`, `.templates/`, and `AGENTS.md` — these will go stale and are architecturally wrong

## Business Goals Identified

- The bundled template source should always resolve the latest agents-smith templates without requiring a new smith release
- Network-based resolution allows template updates to propagate without smith package updates

## Terms to Define (for glossary)

- **Bundled template resolution**: The process by which the default `agents-smith` template source downloads and caches template files from the agents-smith GitHub repository
- **Cache directory**: `~/.cache/smith/` — local storage for downloaded template files to avoid redundant network requests

## Action Items

- [ ] Add `requests` to `pyproject.toml` dependencies
- [ ] Rewrite `BundledTemplateSource` to download from GitHub instead of reading `smith/data/`
- [ ] Add local caching in `~/.cache/smith/agents-smith/`
- [ ] Delete `smith/data/` directory
- [ ] Update technical design doc (stack, module structure, template source resolution section)
- [ ] Update system.md (dependency constraint change)
- [ ] Write ADR for GitHub-based bundled template resolution
- [ ] Update glossary (Agents-Smith entry)