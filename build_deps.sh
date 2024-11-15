#!/usr/bin/env bash
set -e

VENV_DIR=".venv"

# Remove existing venv directory if it exists
if [ -d "$VENV_DIR" ]; then
    echo "Removing existing $VENV_DIR directory..."
    rm -rf "$VENV_DIR"
fi

# Install dependencies into the vendor directory
echo "Installing dependencies into $VENV_DIR..."
poetry install --only=main

echo "Dependencies installed successfully."
