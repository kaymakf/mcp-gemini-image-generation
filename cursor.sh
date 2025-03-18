#!/bin/bash

# Set environment variables from .cursor/mcp.json
export GEMINI_API_KEY="your_gemini_key"

# Define absolute directory path
ABSOLUTE_DIR="/path/to/your/project"

# Change to the project directory
cd "$ABSOLUTE_DIR"
source "$ABSOLUTE_DIR/.venv/bin/activate"
# Option 1: Run with uv directly
uv --directory "$ABSOLUTE_DIR" run mcp run "$ABSOLUTE_DIR/server.py"


