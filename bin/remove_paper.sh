#!/usr/bin/env bash

delete_paper() {
    local parent_dir=$1
    local label=$2

    # Step 1: Remove the .bib entry
    local bib_file="${parent_dir}/bibliography.bib"

    # Find the line number where the label occurs
    local start_line=$(grep -n "@.*${label}" "$bib_file" | cut -d: -f1 | head -n 1)
    
    if [[ -n $start_line ]]; then
        # Find the line number of the next '@' symbol that marks the beginning of the next entry
        local end_line=$(awk 'NR > '"$start_line"' && /^@/ {print NR; exit}' "$bib_file")
        
        # If no next '@' symbol is found, assume deletion till the end of the file
        if [[ -z $end_line ]]; then
            sed -i "${start_line},\$d" "$bib_file"
        else
            # Delete from the start_line to the line just before the end_line
            sed -i "${start_line},$((end_line - 1))d" "$bib_file"
        fi
    else
        echo "Label not found in the .bib file."
        return 1
    fi

    # Step 2: Remove the entry from papers.csv
    local tmp_csv=$(mktemp)
    grep -v "${label}" "${parent_dir}/papers.csv" > "$tmp_csv"
    mv "$tmp_csv" "${parent_dir}/papers.csv"

    # Step 3: Delete the directory
    rm -rf "${parent_dir}/${label}"
}

delete_paper "$1" "$2"
