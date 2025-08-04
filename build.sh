#!/usr/bin/env bash
# Build script for Render

set -o errexit  # Exit on error

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create data directory if it doesn't exist
mkdir -p data
