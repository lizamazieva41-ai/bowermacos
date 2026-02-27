#!/bin/bash
# Bower Antidetect Browser - Run Script
# Supports multiple modes: api, gui, both

cd "$(dirname "$0")"

# Set Python path
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$(pwd)/.venv_lib"

# Default mode
MODE="${1:-api}"

case "$MODE" in
    api)
        echo "Starting API server only..."
        python main.py --mode=api "${@:2}"
        ;;
    gui)
        echo "Starting GUI only..."
        python main.py --mode=gui "${@:2}"
        ;;
    both)
        echo "Starting API server and GUI..."
        python main.py --mode=both "${@:2}"
        ;;
    help|--help|-h)
        echo "Usage: ./run_local.sh [MODE] [OPTIONS]"
        echo ""
        echo "Modes:"
        echo "  api    - Run API server only (default)"
        echo "  gui    - Run GUI only"
        echo "  both   - Run both API and GUI"
        echo ""
        echo "Options:"
        echo "  --host HOST     - API host (default: 0.0.0.0)"
        echo "  --port PORT     - API port (default: 8000)"
        echo ""
        echo "Examples:"
        echo "  ./run_local.sh              # API only"
        echo "  ./run_local.sh api          # API only"
        echo "  ./run_local.sh gui          # GUI only"
        echo "  ./run_local.sh both         # Both API and GUI"
        echo "  ./run_local.sh both --port=9000  # Custom port"
        ;;
    *)
        echo "Unknown mode: $MODE"
        echo "Use './run_local.sh help' for usage information"
        exit 1
        ;;
esac
