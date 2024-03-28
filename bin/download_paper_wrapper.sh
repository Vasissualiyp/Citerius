#!/usr/bin/env bash

source ~/env/venv/bin/activate

# Configuration
parent_dir="$HOME/research/references"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_DIR="$SCRIPT_DIR"
BIN_DIR="$SCRIPT_DIR"

# Function to fetch BibTeX entry
fetch_bibtex() {
    pybibget "$1"
}

obtain_bibtex_info() {
    bibtex_entry="$1"
    echo "$bibtex_entry"
    author=$(echo "$bibtex_entry" | grep author | awk '{print $3}' | tr -cd '[:alpha:]') #Get only last name of the 1st author
    title=$(echo "$bibtex_entry" | grep title | awk '{print $3}' | tr -cd '[:alpha:]') #Get only the 1st title word
    year=$(echo "$bibtex_entry" | grep year | awk '{print $3}' | tr -cd '[0-9]') #Get only the year
    full_author=$(echo "$bibtex_entry" | grep author | awk '{ $1=$2=""; sub(/^  */, ""); print }' | tr -cd '[:alpha:] ') #Get only last name of the 1st author
    full_title=$(echo "$bibtex_entry" | grep title | awk '{ $1=$2=""; sub(/^  */, ""); print }' | tr -cd '[:alpha:] ') #Get only last name of the 1st author
}

print_bibtex_info() {
    bibtex_entry="$1"
	obtain_bibtex_info "$bibtex_entry"
    echo "Full Title: $full_title"
    echo "Full Author: $full_author"
    echo "year: $year"
}

# Function to create a short reference label
create_label() {
    read -p "Enter a label (press Enter for default): " user_label
	if [ -z "$user_label" ]; then
      echo "$1$2$3" 
    else
      echo "$user_label"
    fi
}

# Main script execution
main() {
    read -p "Enter the arXiv number: " arxiv_num
    bibtex_entry=$(fetch_bibtex "$arxiv_num")
    print_bibtex_info "$bibtex_entry"
    
    read -p "Do you want to download this paper? (Y/n): " response
	if [ -z "$response" ]; then
		response="y"
    fi

    read -p "Would you like to download the LaTeX source for this paper? (y/N): " source_download

    label=$(create_label "$author" "$title" "$year")
    
    if [[ $response =~ ^[Yy]$ ]]; then
        "$BIN_DIR/download_paper.sh" "$parent_dir" "$bibtex_entry" "$source_download" "$label" "$arxiv_num"
    else
        echo "Download cancelled."
    fi
}

main
