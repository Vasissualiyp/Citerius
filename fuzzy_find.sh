#!/bin/bash
# Configuration variables
parent_dir="$HOME/research/references"
csv_file="$parent_dir/papers.csv"
bibtex_file="$parent_dir/bibliography.bib"
pdf_dir="$parent_dir/"

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
			zathura "$pdf_file"
        else
            echo "No PDF found in $paper_path."
        fi
    else
        echo "No paper selected."
    fi
}

# Main function
open_paper
