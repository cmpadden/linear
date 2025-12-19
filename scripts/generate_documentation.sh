#!/bin/bash
# Generate Linear CLI documentation from Typer app structure

set -e

echo "Generating Linear CLI documentation..."

uv run typer src/linear/cli.py utils docs \
  --name linear \
  --title "Linear CLI Documentation" \
  --output DOCUMENTATION.md

echo "Successfully generated DOCUMENTATION.md"
