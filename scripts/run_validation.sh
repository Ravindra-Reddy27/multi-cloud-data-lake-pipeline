#!/bin/bash
# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting Data Quality Gate..."
python scripts/validate_data.py