#!/usr/bin/env bash

# Configuration variables for paths
parent_dir="$HOME/research/references" # Directory containing reference materials

# Determine script directory for relative path operations
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_DIR="$SCRIPT_DIR/python"
CITERIUS_DIR="$SCRIPT_DIR/.."
BIN_DIR="$SCRIPT_DIR"

main_wrapper() {
    # Use fzf to select a paper from the CSV file, ignoring the header line
    local label=$($PYTHON_DIR/config.py "$parent_dir")
	echo "$label"
	$BIN_DIR/remove_paper.sh "$parent_dir" "$label"
}

# Call the main function to start the script
main_wrapper
