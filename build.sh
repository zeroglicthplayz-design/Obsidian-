#!/bin/bash
set -e

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install Flask

echo "Dependencies installed successfully!"
