# ADR_20260502_archive-prefix-stripping

## Status

Accepted

## Context

GitHub archives and many tar/zip files contain a single top-level directory (e.g., temple8-main/) that wraps all entries. If smith writes files preserving this prefix, they would be nested one level deep instead of at the project root where they belong.

## Interview

| Question | Answer |
|---|---|
| Should the top-level directory be stripped? | Yes — smith should write files at the project root, not nested under the repo folder |
| What if the archive has multiple top-level directories? | No stripping — write entries as-is |

## Decision

Detect if all archive entries share a single common top-level directory and, if so, strip that prefix. This is handled by `_detect_top_dir`.

## Reason

GitHub archives always have a top-level directory like `repo-main/` or `repo-master/`. Stripping it places files at the project root where they belong, matching the project layout that smith expects.

## Alternatives Considered

- **Never strip prefix**: Would require users to nest their templates in an extra directory, or always get a nested result
- **Require a --strip-prefix flag**: Adds CLI complexity for a problem that can be auto-detected

## Consequences

- (+) Archives "just work" — no manual prefix configuration needed
- (+) Consistent with user expectations (files land at project root)
- (-) Rare archives with multiple top-level directories will write files with their full path, which may be unexpected

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Accepted? |
|------|------------|--------|------------|-----------|
| Archive with multiple top-level dirs produces unexpected paths | Low | Low | _detect_top_dir returns None in this case, preserving original paths | Yes |