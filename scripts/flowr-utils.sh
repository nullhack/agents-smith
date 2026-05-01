#!/bin/bash

# Utility script for working with flowr flows
# Usage: ./scripts/flowr-utils.sh [validate|view|list] [FLOW_NAME]

set -e

FLOWS_DIR=".flowr/flows"

# Check if we're in venv (look for flowr)
if ! source .venv/bin/activate 2>/dev/null || ! python -c "import flowr" 2>/dev/null; then
    echo "Error: flowr not available. Make sure you're in the project directory and have activated the venv"
    echo "Run: source .venv/bin/activate"
    exit 1
fi

# Activate venv
source .venv/bin/activate

show_usage() {
    echo "Usage: $0 [validate|view|list|graph] [FLOW_NAME]"
    echo ""
    echo "Commands:"
    echo "  validate [FLOW]  - Validate flow definition(s)"
    echo "  view [FLOW]      - View flow as mermaid diagram"
    echo "  list             - List all available flows"
    echo "  graph            - Generate interactive D3.js visualization"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 validate main-flow"
    echo "  $0 view tdd-cycle-flow"
    echo "  $0 validate  # validates all flows"
    echo "  $0 graph     # generates .flowr/graph/index.html"
}

list_flows() {
    echo "Available flowr flows:"
    for yaml_file in "${FLOWS_DIR}"/*.yaml; do
        if [[ -f "$yaml_file" ]]; then
            flow_name=$(basename "$yaml_file" .yaml)
            echo "  - $flow_name"
        fi
    done
}

validate_flow() {
    local flow_name="$1"
    local yaml_file="${FLOWS_DIR}/${flow_name}.yaml"
    
    if [[ ! -f "$yaml_file" ]]; then
        echo "Error: Flow '$flow_name' not found at $yaml_file"
        exit 1
    fi
    
    echo "Validating $flow_name..."
    python -m flowr validate "$yaml_file"
}

view_flow() {
    local flow_name="$1"
    local yaml_file="${FLOWS_DIR}/${flow_name}.yaml"
    
    if [[ ! -f "$yaml_file" ]]; then
        echo "Error: Flow '$flow_name' not found at $yaml_file"
        exit 1
    fi
    
    echo "Mermaid diagram for $flow_name:"
    echo "================================"
    python -m flowr mermaid "$yaml_file"
}

generate_graph() {
    echo "Generating interactive D3.js visualization..."
    python scripts/generate-graph.py
}

validate_all() {
    echo "Validating all flows..."
    for yaml_file in "${FLOWS_DIR}"/*.yaml; do
        if [[ -f "$yaml_file" ]]; then
            flow_name=$(basename "$yaml_file" .yaml)
            echo ""
            validate_flow "$flow_name"
        fi
    done
}

# Main logic
case "${1:-}" in
    "list")
        list_flows
        ;;
    "validate")
        if [[ -n "${2:-}" ]]; then
            validate_flow "$2"
        else
            validate_all
        fi
        ;;
    "view")
        if [[ -z "${2:-}" ]]; then
            echo "Error: Flow name required for view command"
            show_usage
            exit 1
        fi
        view_flow "$2"
        ;;
    "graph")
        generate_graph
        ;;
    "-h"|"--help"|"")
        show_usage
        ;;
    *)
        echo "Error: Unknown command '$1'"
        show_usage
        exit 1
        ;;
esac