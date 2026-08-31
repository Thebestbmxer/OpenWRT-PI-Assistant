#!/bin/bash
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "Router Pi Controller Development Setup"
echo "=========================================="
echo

if [ ! -f /etc/debian_version ]; then
    echo "Error: Debian-based system required for Debian package development."
    exit 1
fi

echo "Installing Debian build dependencies..."

sudo apt update
sudo apt build-dep .

echo
echo "Installing packaging tools..."

sudo apt install -y \
    build-essential \
    devscripts

echo
echo "Development environment ready."
echo
echo "Run tests:"
echo "  pytest -v"
echo
echo "Build package:"
echo "  dpkg-buildpackage -us -uc -b"
