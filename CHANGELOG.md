# Changelog

> *Clone AI agent configurations into any project.*

All notable changes to agents-smith will be documented in this file.

## [1.0.0] - cloned Neo - 20260502

### Changed

- **First major release** — stable API for `smith clone` and `smith purge`
- **Breaking:** `smith connect` renamed to `smith clone` — the command that fetches template files and writes them to a project
- **Breaking:** `smith disconnect` renamed to `smith purge` — the command that removes smith-managed files
- Complete documentation rewrite: specs, features, ADRs, glossary, domain model, technical design, context map
- Matrix/Agent Smith visual identity: green phosphor palette, S scan-line lettermark, dark void backgrounds
- README redesigned with banner, badges, architecture diagram, and command reference

## [0.2.0] - 20260501

### Added

- `smith clone` command: fetches agentic files (AGENTS.md, .opencode/, .flowr/, .templates/) from a template source and writes them to a project
- `smith purge` command: removes smith-managed files by reading the managed .gitignore section
- Source resolution: CLI `--source` flag > `[tool.smith] source` in pyproject.toml > default `github:nullhack/temple8`
- GitHub shorthand support: `github:user/repo` resolves to archive download
- HTTP URL support: zip and tar.gz archives
- Local directory support: walk a local path for template files
- `--overwrite` flag on clone: replaces existing files and directories when set
- `.gitignore` section management: start/end markers (`# smith managed` / `# end smith managed`) for idempotent tracking
- Allowed topics filter: only files matching `AGENTS.md`, `.opencode/`, `.flowr/`, `.templates/` are written
- Archive prefix stripping: detects and removes single common top-level directory from archives