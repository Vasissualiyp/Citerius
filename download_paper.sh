#!/bin/bash

# Configuration
bibtex_file="path/to/your/bibtex_file.bib"
csv_file="path/to/your/csv_file.csv"
paper_storage="path/to/your/paper_storage"

# Function to fetch BibTeX entry
fetch_bibtex() {
    pybibget "$1"
}

# Function to create a short reference label
create_label() {
    echo "$1" | awk -F ' and ' '{print $NF}' | awk '{print $NF "_" $NF}' | tr -d ','
}

# Function to append BibTeX entry to file
append_bibtex() {
    echo "$1" >> "$bibtex_file"
}

# Function to create a directory for the paper
create_directory() {
    mkdir -p "$paper_storage/$1"
}

# Function to download the paper
download_paper() {
    # Add your paper download command here
    echo "Downloading paper to $paper_storage/$1"
}

# Function to update CSV file
update_csv() {
    # Add CSV update logic here
    echo "$1,$2,$paper_storage/$2" >> "$csv_file"
}

# Main script execution
read -p "Enter the arXiv number: " arxiv_num
bibtex_entry=$(fetch_bibtex "$arxiv_num")
title=$(echo "$bibtex_entry" | grep -oP 'title = \{\K[^}]+' )
author=$(echo "$bibtex_entry" | grep -oP 'author = \{\K[^}]+' | cut -d ',' -f 1)

echo "Title: $title"
echo "Author: $author"
read -p "Do you want to download this paper? (y/n): " response

if [[ $response =~ ^[Yy]$ ]]; then
    label=$(create_label "$author")
    append_bibtex "$bibtex_entry"
    create_directory "$label"
    download_paper "$label"
    update_csv "$title,$author" "$label"
    echo "Paper processing completed."
else
    echo "Download cancelled."
fi
