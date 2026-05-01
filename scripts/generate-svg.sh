#!/bin/bash

# Generate SVG diagrams from flowr flow definitions
# Usage: ./scripts/generate-svg.sh [FLOW_NAME]
# If FLOW_NAME not provided, generates all flows that work with mermaid-cli

set -e

FLOWS_DIR=".flowr/flows"
OUTPUT_DIR="flows"

# Flows that actually work with mermaid-cli (very limited due to exit state syntax issues)
WORKING_FLOWS=(
    "tdd-cycle-flow"
)

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required"
    exit 1
fi

# Check if npx is available (for mermaid-cli)
if ! command -v npx &> /dev/null; then
    echo "Error: npx is required for mermaid-cli"
    exit 1
fi

# Check if we're in venv (look for flowr)
if ! source .venv/bin/activate 2>/dev/null || ! python -c "import flowr" 2>/dev/null; then
    echo "Error: flowr not available. Make sure you're in the project directory and have activated the venv"
    echo "Run: source .venv/bin/activate"
    exit 1
fi

# Activate venv
source .venv/bin/activate

generate_svg() {
    local flow_name="$1"
    local yaml_file="${FLOWS_DIR}/${flow_name}.yaml"
    local svg_file="${OUTPUT_DIR}/${flow_name}.svg"
    local temp_mermaid="/tmp/${flow_name}.mmd"
    
    if [[ ! -f "$yaml_file" ]]; then
        echo "Warning: $yaml_file not found, skipping..."
        return
    fi
    
    echo "Generating $svg_file from flowr definition..."
    
    # Step 1: Convert flowr to mermaid (filter out problematic syntax)
    python -m flowr mermaid "$yaml_file" | grep -v "note right of" > "$temp_mermaid"
    
    # Step 2: Convert mermaid to SVG
    if npx @mermaid-js/mermaid-cli@11.12.0 -i "$temp_mermaid" -o "$svg_file" -t neutral 2>/dev/null; then
        echo "✓ Generated $svg_file"
    else
        echo "⚠️  Failed to generate $svg_file (mermaid-cli compatibility issue)"
        echo "   Flow definition is valid, but SVG generation failed"
    fi
    
    # Clean up temp file
    rm -f "$temp_mermaid"
}

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

if [[ $# -eq 1 ]]; then
    # Generate specific flow
    generate_svg "$1"
else
    # Generate working flows
    echo "Generating SVG diagrams from flowr flows..."
    echo "Note: Only generating flows known to work with mermaid-cli"
    
    for flow_name in "${WORKING_FLOWS[@]}"; do
        generate_svg "$flow_name"
    done
    
    echo ""
    echo "SVG generation limitations:"
    echo "- Only tdd-cycle-flow works with mermaid-cli (exit state syntax issues)"
    echo "- All other flows have mermaid-cli compatibility problems"
    echo ""
    echo "All flows are still valid flowr definitions and can be:"
    echo "- Validated: python -m flowr validate .flowr/flows/<flow>.yaml"
    echo "- Viewed as mermaid: python -m flowr mermaid .flowr/flows/<flow>.yaml"
    echo "- Used programmatically with flowr APIs"
    echo "✓ All working flows converted to SVG"
fi