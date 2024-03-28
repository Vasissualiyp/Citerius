#!/usr/bin/env bash

# Configuration variables
parent_dir="$1"
label="$2"
csv_file="$parent_dir/papers.csv"
bibtex_file="$parent_dir/bibliography.bib"
pdf_dir="$parent_dir"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CITERIUS_DIR="$SCRIPT_DIR/.."
BIN_DIR="$SCRIPT_DIR"

open_pdf() {
    echo "Choose the application to open the PDF:"
    echo "z: Zathura"
    echo "x: Xournalpp"
    read -p "Enter your choice (z/x): " choice

	# Set default choice to 'z' if no input is provided
    if [[ -z "$choice" ]]; then
        choice='z'
    fi

    case $choice in
        z)
            zathura "$1" &
            ;;
        x)
            label=$(basename "$1" .pdf)
            "$BIN_DIR/open_with_xopp.sh" "$label"
            ;;
        *)
            echo "Invalid choice. Please enter 'z' or 'x'."
            ;;
    esac
}

find_line_by_exact_label() {
    local label="$1"
    local csv_file="$2"
    # Extract the 5th column and find the exact match, then get the line number
    local line_number=$(awk -F',' '{print $5}' "$csv_file" | grep -nxF "\"$label\"" | cut -d: -f1)

    # Adjust line_number to account for any headers you might have skipped
    # For example, if you skipped one header line, you should:
    # line_number=$((line_number + 1))

    if [[ -n $line_number ]]; then
        # Extract the specific line from the csv file
        sed "${line_number}q;d" "$csv_file"
    else
        echo "Label not found."
    fi
}

# Function to search and open a paper
open_paper() {
	local selected_paper=$(find_line_by_exact_label "$label" "$csv_file")
    local relative_path=$(echo $selected_paper | cut -d ',' -f 5 | sed 's/"//g')
	echo "$relative_path"

    if [[ -n $selected_paper ]]; then
        local paper_path="${pdf_dir}/${relative_path}"
        local pdf_file=$(find "$paper_path" -maxdepth 1 -type f -name '*.pdf' | head -n 1)

        if [[ -n $pdf_file ]]; then
            echo "Opening $pdf_file" # Replace this with your PDF reader command
			open_pdf "$pdf_file"
        else
            echo "No PDF found in $paper_path."
        fi
    else
        echo "No paper selected."
    fi
}

# Main function
open_paper
