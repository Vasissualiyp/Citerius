#!/bin/bash

source ~/env/venv/bin/activate

# Configuration
parent_dir="$HOME/research/references"
csv_file="$parent_dir/papers.csv"
bibtex_file="$parent_dir/bibliography.bib"
pdf_dir="$parent_dir"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_DIR="$SCRIPT_DIR"

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

download_paper_and_source() {
    bibtex_entry="$1"
    source_download="$2"

    label=$(create_label "$author" "$title" "$year")
	echo "$label"
    download_name="$label.pdf"

	paper_specific_dir="$pdf_dir/$label"
	bibtex_modified_entry=$(change_bibtex_ref "$bibtex_entry" "$label" "$arxiv_num")
    append_bibtex "$bibtex_modified_entry"

    mkdir -p "$paper_specific_dir"
    if [ ! -f "$paper_specific_dir/$download_name" ]; then
        download_paper "$arxiv_num" "$paper_specific_dir" "$download_name" "notsource"
        update_csv "$full_title" "$full_author" "$arxiv_num" "$year" "$label"
    else
		read -p "The paper was already downloaded. Overwrite? (y/n): " overwrite
        if [[ $overwrite =~ ^[Yy]$ ]]; then
				rm -f "$paper_specific_dir/$download_name"
				download_paper "$arxiv_num" "$paper_specific_dir" "$download_name" "notsource"
		fi
    fi

    if [[ $source_download  =~ ^[Yy]$ ]]; then
		echo "In the srcdwnload loop"
		mkdir -p "$paper_specific_dir/src"
        download_name="$label.tar.gz"
        download_paper "$arxiv_num" "$paper_specific_dir/src" "$download_name" "source"
		cd "$paper_specific_dir/src" 
		tar -xvf *.gz
		rm *.gz
		echo "Untared the source successfully"
    fi

    echo "Paper processing completed."
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

# Change the titular bibtex reference from arxiv number to the label
change_bibtex_ref() {
    bibtex_string="$1"
    label="$2"
    arxiv_no="$3"

    # Replace "{arxiv_no" with "{label" in the bibtex entry
    echo "$bibtex_string" | sed -e "s/{${arxiv_no}/{${label}/"
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
    download_source="$4"
    echo "Downloading paper to $paper_download_loc"
	python "$PYTHON_DIR/download_arxiv_paper.py" "$arxiv_num" "$paper_download_loc" "$download_name" "$download_source"
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
main() {
    read -p "Enter the arXiv number: " arxiv_num
    bibtex_entry=$(fetch_bibtex "$arxiv_num")
    print_bibtex_info "$bibtex_entry"
    
    read -p "Do you want to download this paper? (Y/n): " response
	if [ -z "$response" ]; then
		response="y"
    fi

    read -p "Would you like to download the LaTeX source for this paper? (y/N): " source_download
    
    if [[ $response =~ ^[Yy]$ ]]; then
        download_paper_and_source "$bibtex_entry" "$source_download"
    else
        echo "Download cancelled."
    fi
}

main
