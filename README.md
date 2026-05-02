# agents-smith

Clone AI agent configurations (AGENTS.md, .opencode/, .flowr/, .templates/) to any project.

## Install

```bash
pip install agents-smith
```

## Usage

```bash
# Clone — downloads templates from the default source (temple8)
smith clone

# Clone from a specific source
smith clone --source github:myorg/my-template
smith clone --source /path/to/local/template
smith clone --source https://example.com/template.zip

# Clone and overwrite existing files
smith clone --overwrite

# Purge — removes files listed in the smith-managed .gitignore section
smith purge
```

## Source resolution

1. `--source` CLI flag (highest priority)
2. `[tool.smith] source = "..."` in pyproject.toml
3. Default: `github:nullhack/temple8`

## How it works

**clone**: Downloads AGENTS.md, .opencode/, .flowr/, .templates/ from the source. Skips any file or directory that already exists unless `--overwrite` is set. Adds a `# smith managed` section to .gitignore listing what was written.

**purge**: Reads the smith-managed section in .gitignore and deletes every file/directory listed there. Does not remove the .gitignore section itself.

## .gitignore section

```
# smith managed
AGENTS.md
.opencode/
.flowr/
.templates/
# end smith managed
```

Only items listed in this section are deleted on purge. Edit this section to control what smith manages.