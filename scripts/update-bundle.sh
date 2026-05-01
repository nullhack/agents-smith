#!/usr/bin/env bash
# Update smith/data/ with agentic files from the agents-smith v8_release branch.
# Usage: ./scripts/update-bundle.sh
#
# Downloads the agents-smith v8_release archive from GitHub,
# extracts it, and copies only the agentic files to smith/data/.
# Agentic files: AGENTS.md, .opencode/agents/, .opencode/skills/,
#   .opencode/knowledge/, .opencode/tools/, .templates/, .flowr/

set -euo pipefail

TEMP_DIR=$(mktemp -d)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DATA_DIR="$PROJECT_ROOT/smith/data"

echo "Downloading agents-smith v8_release archive..."
curl -sL "https://github.com/nullhack/agents-smith/archive/refs/heads/v8_release.tar.gz" \
    -o "$TEMP_DIR/agents-smith.tar.gz"

echo "Extracting archive..."
tar -xzf "$TEMP_DIR/agents-smith.tar.gz" -C "$TEMP_DIR"

SRC_DIR="$TEMP_DIR/agents-smith-v8_release"

if [ ! -d "$SRC_DIR" ]; then
    echo "ERROR: Expected directory agents-smith-v8_release not found in archive"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "Removing old agentic files from smith/data/..."
rm -rf "$DATA_DIR/AGENTS.md" "$DATA_DIR/.opencode" "$DATA_DIR/.templates" "$DATA_DIR/.flowr"

echo "Copying AGENTS.md..."
cp "$SRC_DIR/AGENTS.md" "$DATA_DIR/AGENTS.md"

echo "Copying .opencode/ subdirectories (agents, skills, knowledge, tools)..."
mkdir -p "$DATA_DIR/.opencode"
for subdir in agents skills knowledge tools; do
    if [ -d "$SRC_DIR/.opencode/$subdir" ]; then
        cp -r "$SRC_DIR/.opencode/$subdir" "$DATA_DIR/.opencode/$subdir"
        echo "  Copied .opencode/$subdir/"
    else
        echo "  Skipped .opencode/$subdir/ (not found in source)"
    fi
done

echo "Copying .templates/..."
cp -r "$SRC_DIR/.templates" "$DATA_DIR/.templates"

echo "Copying .flowr/..."
cp -r "$SRC_DIR/.flowr" "$DATA_DIR/.flowr"

echo "Cleaning up..."
rm -rf "$TEMP_DIR"

echo "Done. smith/data/ updated from agents-smith v8_release."
echo "Files in smith/data/:"
find "$DATA_DIR" -not -name '__init__.py' -not -path "$DATA_DIR/__init__.py" -type f | head -20
echo "..."
TOTAL=$(find "$DATA_DIR" -type f | wc -l)
echo "Total files: $TOTAL"
SIZE=$(du -sh "$DATA_DIR" | cut -f1)
echo "Total size: $SIZE"