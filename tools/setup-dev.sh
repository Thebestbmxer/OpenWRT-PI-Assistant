#!/bin/bash
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$PROJECT_ROOT"

echo "Creating Python virtual environment..."

python3 -m venv .venv

echo "Installing project and test dependencies..."

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[test]"

echo "Development environment ready."
echo
echo "Run tests with:"
echo "  .venv/bin/pytest -v"