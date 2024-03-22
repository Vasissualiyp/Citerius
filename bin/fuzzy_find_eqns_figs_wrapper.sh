#!/usr/bin/env bash

# Configuration variables for paths
parent_dir="$HOME/research/references" # Directory containing reference materials

# Determine script directory for relative path operations
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CITERIUS_DIR="$SCRIPT_DIR/.."
BIN_DIR="$SCRIPT_DIR"

main_wrapper() {
    # Use fzf to select a paper from the CSV file, ignoring the header line
    local label=$($BIN_DIR/fuzzy_find_script.sh "$parent_dir")
    echo "LEGEND: f for figures, e for equations, followed by the number of item"
    read -p "Enter the items you want to find (e.g., 'f5 e12' for 5th figure and 12th equation): " input_line
	$BIN_DIR/fuzzy_find_eqns_figs.sh "$parent_dir" "$label" "$input_line"
}

# Call the main function to start the script
main_wrapper
