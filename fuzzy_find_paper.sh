#!/usr/bin/env bash

# Configuration variables
parent_dir="$HOME/research/references"
csv_file="$parent_dir/papers.csv"
bibtex_file="$parent_dir/bibliography.bib"
pdf_dir="$parent_dir"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CITERIUS_DIR="$SCRIPT_DIR"

open_pdf() {
    echo "Choose the application to open the PDF:"
    echo "z: Zathura"
    echo "x: Xournalpp"
    read -p "Enter your choice (z/x): " choice

    case $choice in
        z)
            zathura "$1" &
            ;;
        x)
            label=$(basename "$1" .pdf)
            "$CITERIUS_DIR/open_with_xopp.sh" "$label"
            ;;
        *)
            echo "Invalid choice. Please enter 'z' or 'x'."
            ;;
    esac
}

# Function to search and open a paper
open_paper() {
    local selected_paper=$(cat "$csv_file" | sed '1d' | fzf --delimiter=',' --with-nth=1,2,3,4,5)
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
