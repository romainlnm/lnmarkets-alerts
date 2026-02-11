#!/bin/bash
# Wrapper to run LN Markets scripts with credentials from .env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Load .env if it exists
if [ -f "$SKILL_DIR/.env" ]; then
    export $(grep -v '^#' "$SKILL_DIR/.env" | xargs)
fi

# Run the requested script
python3 "$SCRIPT_DIR/$1" "${@:2}"
