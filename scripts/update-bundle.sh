#!/usr/bin/env bash
# Update smith/data/ with agentic files from the temple8 main branch.
# Usage: ./scripts/update-bundle.sh
#
# Downloads the temple8 main archive from GitHub,
# extracts it, and copies only the agentic files to smith/data/.
# Agentic files: AGENTS.md, .opencode/agents/, .opencode/skills/,
#   .opencode/knowledge/, .opencode/tools/, .templates/, .flowr/

set -euo pipefail

TEMP_DIR=$(mktemp -d)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DATA_DIR="$PROJECT_ROOT/smith/data"

echo "Downloading temple8 main archive..."
curl -sL "https://github.com/nullhack/temple8/archive/refs/heads/main.tar.gz" \
    -o "$TEMP_DIR/temple8.tar.gz"

echo "Extracting archive..."
tar -xzf "$TEMP_DIR/temple8.tar.gz" -C "$TEMP_DIR"

SRC_DIR="$TEMP_DIR/temple8-main"

if [ ! -d "$SRC_DIR" ]; then
    echo "ERROR: Expected directory temple8-main not found in archive"
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

echo "Done. smith/data/ updated from temple8 main."
echo "Files in smith/data/:"
find "$DATA_DIR" -not -name '__init__.py' -not -path "$DATA_DIR/__init__.py" -type f | head -20
echo "..."
TOTAL=$(find "$DATA_DIR" -type f | wc -l)
echo "Total files: $TOTAL"
SIZE=$(du -sh "$DATA_DIR" | cut -f1)
echo "Total size: $SIZE"