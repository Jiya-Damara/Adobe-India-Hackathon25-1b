#!/bin/bash

# Simple Docker setup for Challenge 1B

set -e

echo "Building Docker image..."
docker build -t challenge1b-processor .

echo "Running process_pdfs.py through Docker..."
docker run --rm -v "$(pwd)":/app challenge1b-processor

echo "Done! Check Collection folders for output files."
