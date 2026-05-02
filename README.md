<div align="center">

<img src="docs/assets/banner.svg" alt="agents-smith" width="100%"/>

<br/><br/>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?style=for-the-badge)](https://nullhack.github.io/agents-smith/coverage/)
[![CI](https://img.shields.io/github/actions/workflow/status/nullhack/agents-smith/ci.yml?style=for-the-badge&label=CI)](https://github.com/nullhack/agents-smith/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-%E2%89%A513.0-blue?style=for-the-badge)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/agents-smith?color=%2300FF41&style=for-the-badge)](https://pypi.org/project/agents-smith/)

**One command to clone AI agent configurations into any project. One command to purge them.**

</div>

---

You have used AI coding assistants. You have copied `.opencode/`, `.flowr/`, `AGENTS.md`, and `.templates/` into projects by hand — or asked your team to do the same, over and over, across every repository. Files drift out of sync. Versions scatter. Onboarding a new repo means ten minutes of manual file wrangling before the first prompt.

**smith enters a project, copies its patterns, and returns something more capable than what it found.**

Two commands. No configuration files in your project. No framework overhead. No leftover files after removal.

---

## Who is this for?

### Developers — Stop copying AI config files between projects

You set up opencode, flowr, and agent templates in one project. Then you do it again. And again. `smith clone` pulls the exact same configuration from any GitHub repo, local directory, or URL into your project in one step. `smith purge` removes every file and every gitignore entry — no orphans, no stale references.

### Teams — Consistent agent configurations across every repository

Every team member runs the same `smith clone` command and gets the same AGENTS.md, the same .opencode agents, the same .flowr workflows. No "it works on my machine." When the template updates, clone again with `--overwrite`. When a project no longer needs agentic tooling, `smith purge` and move on.

---

## What it does

```
smith clone    →  fetches AGENTS.md, .opencode/, .flowr/, .templates/ into your project
smith purge    →  removes every smith-managed file and directory
```

**Safety boundary.** Only files matching allowed topics are ever written — regardless of what the source archive contains. Your project never receives arbitrary files.

**Clean removal.** Purge reads the managed section in `.gitignore` and deletes exactly what is listed there. The section itself is preserved so you can clone again later.

**Source resolution.** Three ways to specify where templates come from:

| Priority | Source | Example |
|----------|--------|---------|
| 1 — CLI flag | `--source` | `smith clone --source github:myorg/templates` |
| 2 — Config | `[tool.smith] source` in pyproject.toml | `source = "github:myorg/templates"` |
| 3 — Default | `github:nullhack/temple8` | Used when no flag or config is set |

---

## Quick start

```bash
pip install agents-smith
smith clone                                      # default source (temple8)
smith purge                                      # remove everything
```

That is it. Two commands. No setup, no config file, no framework.

---

## Commands

### `smith clone`

```bash
smith clone                                    # default source
smith clone --source github:myorg/templates    # GitHub shorthand
smith clone --source /path/to/local/template    # local directory
smith clone --source https://example.com/t.zip  # URL to archive
smith clone --overwrite                         # replace existing files
```

Fetches template files from a source, filters by allowed topics, writes them to the project directory, and adds a managed section to `.gitignore`. Existing files are skipped unless `--overwrite` is passed.

### `smith purge`

```bash
smith purge    # removes all smith-managed files
```

Reads the smith-managed section in `.gitignore` and deletes every file and directory listed there. The `.gitignore` section itself is preserved so you can clone again later.

---

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

---

## Architecture

```
smith/
├── cli.py         # CLI — argparse, subcommands (clone, purge)
├── core.py        # Domain — resolve_source, fetch, clone, purge, FileSpec
└── gitignore.py   # Infrastructure — .gitignore section management
```

Flat module structure. Two commands. No framework overhead.

---

## License

MIT — see [LICENSE](LICENSE).

**Author:** [@nullhack](https://github.com/nullhack) · [Documentation](https://nullhack.github.io/agents-smith)

<!-- MARKDOWN LINKS -->
[contributors-shield]: https://img.shields.io/github/contributors/nullhack/agents-smith.svg?style=for-the-badge
[contributors-url]: https://github.com/nullhack/agents-smith/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/nullhack/agents-smith.svg?style=for-the-badge
[forks-url]: https://github.com/nullhack/agents-smith/network/members
[stars-shield]: https://img.shields.io/github/stars/nullhack/agents-smith.svg?style=for-the-badge
[stars-url]: https://github.com/nullhack/agents-smith/stargazers
[issues-shield]: https://img.shields.io/github/issues/nullhack/agents-smith.svg?style=for-the-badge
[issues-url]: https://github.com/nullhack/agents-smith/issues
[license-shield]: https://img.shields.io/badge/license-MIT-green?style=for-the-badge
[license-url]: https://github.com/nullhack/agents-smith/blob/main/LICENSE