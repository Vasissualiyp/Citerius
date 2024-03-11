#!/bin/bash

source ~/env/venv/bin/activate

# Configuration
parent_dir="$HOME/research/references"
csv_file="$parent_dir/papers.csv"
bibtex_file="$parent_dir/bibliography.bib"
pdf_dir="$parent_dir"

# Function to fetch BibTeX entry
fetch_bibtex() {
    pybibget "$1"
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
	arxiv_num="$1"
    echo "$arxiv_num"
	paper_download_loc="$2"
    echo "$paper_download_loc"
    download_name="$3"
    echo "$download_name"
    echo "Downloading paper to $paper_download_loc"
	echo "python download_arxiv_paper.py $arxiv_num $paper_download_loc $download_name"
	python download_arxiv_paper.py "$arxiv_num" "$paper_download_loc" "$download_name"
}

# Function to update CSV file
update_csv() {
    # Check if CSV file exists, if not, create and add header
    if [ ! -f "$csv_file" ]; then
        echo 'Title,Author,ArXiv Number,Year,Label' > "$csv_file"
    fi

    # Format the input data and append to CSV, ensuring values are enclosed in quotes
    local formatted_entry="\"$1\",\"$2\",\"$3\",\"$4\",\"$5\""
    echo "$formatted_entry" >> "$csv_file"
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
    download_name="$label.pdf"

	paper_specific_dir="$pdf_dir/$label"
    append_bibtex "$bibtex_entry"

    mkdir -p "$paper_specific_dir"
    download_paper "$arxiv_num" "$paper_specific_dir" "$download_name"

    update_csv "$full_title" "$full_author" "$arxiv_num" "$year" "$label"
    echo "Paper processing completed."
else
    echo "Download cancelled."
fi
