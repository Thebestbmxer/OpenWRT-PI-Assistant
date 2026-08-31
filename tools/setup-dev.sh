#!/bin/bash
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$PROJECT_ROOT"

echo "Installing Debian build dependencies..."

sudo apt update
sudo apt build-dep .

echo
echo "Development environment ready."
echo
echo "Run tests with:"
echo "  pytest -v"
echo
echo "Build the Debian package with:"
echo "  dpkg-buildpackage -us -uc -b"
