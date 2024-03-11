#!/bin/bash

source ~/env/venv/bin/activate

# Configuration
parent_dir="$HOME/research/references"
csv_file="$parent_dir/papers.csv"
bibtex_file="$parent_dir/bibliography.bib"
pdf_dir="$parent_dir/"

# Function to fetch BibTeX entry
fetch_bibtex() {
    pybibget "$1"
}

# Function to create a short reference label
create_label() {
    echo "$1$2$3" 
}

# Function to append BibTeX entry to file
append_bibtex() {
    echo "$1" >> "$bibtex_file"
}

# Function to create a directory for the paper
create_directory() {
    mkdir -p "$pdf_dir/$1"
}

# Function to download the paper
download_paper() {
    # Add your paper download command here
    echo "Downloading paper to $pdf_dir/$1"
}

# Function to update CSV file
update_csv() {
    # Add CSV update logic here
    echo "$1,$2,$pdf_dir/$2" >> "$csv_file"
}

# Main script execution
read -p "Enter the arXiv number: " arxiv_num
bibtex_entry=$(fetch_bibtex "$arxiv_num")
echo "$bibtex_entry"
author=$(echo "$bibtex_entry" | grep author | awk '{print $3}' | tr -cd '[:alpha:]') #Get only last name of the 1st author
title=$(echo "$bibtex_entry" | grep title | awk '{print $3}' | tr -cd '[:alpha:]') #Get only the 1st title word
year=$(echo "$bibtex_entry" | grep year | awk '{print $3}' | tr -cd '[0-9]') #Get only the year
full_author=$(echo "$bibtex_entry" | grep author | awk '{ $1=$2=""; sub(/^  */, ""); print }' | tr -cd '[:alpha:] ') #Get only last name of the 1st author
full_title=$(echo "$bibtex_entry" | grep title | awk '{ $1=$2=""; sub(/^  */, ""); print }' | tr -cd '[:alpha:] ') #Get only last name of the 1st author

echo "Full Title: $full_title"
echo "Full Author: $full_author"
echo "year: $year"
read -p "Do you want to download this paper? (y/n): " response

if [[ $response =~ ^[Yy]$ ]]; then
    label=$(create_label "$author" "$title" "$year")
	echo "$label"
	exit 0
    append_bibtex "$bibtex_entry"
    create_directory "$label"
    download_paper "$label"
    update_csv "$title,$author" "$label"
    echo "Paper processing completed."
else
    echo "Download cancelled."
fi
