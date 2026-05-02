<div align="center">
  <img src="docs/assets/banner.svg" alt="smith — Clone AI agent configurations into any project" width="800">
</div>

<br>

<p align="center">
  <strong>Clone AI agent configurations into any project.</strong><br>
  <code>smith clone</code> fetches AGENTS.md, .opencode/, .flowr/, .templates/ from any source.<br>
  <code>smith purge</code> removes them cleanly. No leftovers.
</p>

<p align="center">
  <a href="https://pypi.org/project/agents-smith/"><img src="https://img.shields.io/pypi/v/agents-smith?color=%2300FF41&label=pypi&style=flat-square" alt="PyPI"></a>
  <a href="https://github.com/nullhack/agents-smith/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-%2300FF41?style=flat-square" alt="License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-%E2%89%A513.0-%2300FF41?style=flat-square" alt="Python"></a>
</p>

---

## Install

```bash
pip install agents-smith
```

## Quick start

```bash
# Clone the default template (temple8) into your project
smith clone

# Purge all smith-managed files when you're done
smith purge
```

That's it. AGENTS.md, .opencode/, .flowr/, and .templates/ appear in your project, tracked in .gitignore. When you're done, `smith purge` removes every file and directory — no orphan files, no stale .gitignore entries.

## Source resolution

| Priority | Source | Example |
|----------|--------|---------|
| 1 — CLI flag | `--source` | `smith clone --source github:myorg/templates` |
| 2 — Config | `[tool.smith] source` in pyproject.toml | `source = "github:myorg/templates"` |
| 3 — Default | `github:nullhack/temple8` | Used when no flag or config is set |

## Commands

### `smith clone`

Fetches template files from a source, filters them by allowed topics, writes them to the project directory, and adds a managed section to .gitignore.

```bash
smith clone                                    # default source
smith clone --source github:myorg/templates    # GitHub shorthand
smith clone --source /path/to/local/template   # local directory
smith clone --source https://example.com/t.zip # URL to archive
smith clone --overwrite                        # replace existing files
```

**Safety:** Only files matching allowed topics (AGENTS.md, .opencode/, .flowr/, .templates/) are ever written. Existing files and directories are skipped unless `--overwrite` is passed.

### `smith purge`

Reads the smith-managed section in .gitignore and deletes every file and directory listed there. The .gitignore section itself is preserved so you can clone again later.

```bash
smith purge    # removes all smith-managed files
```

## .gitignore section

```gitignore
# smith managed
AGENTS.md
.opencode/
.flowr/
.templates/
# end smith managed
```

Only items in this section are removed on purge. Edit it to control what smith manages.

## Architecture

```
smith/
├── cli.py         # CLI — argparse, subcommands (clone, purge)
├── core.py        # Domain — resolve_source, fetch, clone, purge, FileSpec
└── gitignore.py   # Infrastructure — .gitignore section management
```

Flat module structure. Two commands. No framework overhead. The allowed-topics list is a compile-time safety boundary — only agentic configuration files are ever written to your project, regardless of what the source archive contains.

## License

MIT