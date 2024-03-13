#!/usr/bin/env bash

# Configuration variables
parent_dir="$HOME/research/references"
csv_file="$parent_dir/papers.csv"
bibtex_file="$parent_dir/bibliography.bib"
pdf_dir="$parent_dir"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CITERIUS_DIR="$SCRIPT_DIR"

choose_from_multiple_tex_files() {
	if [ "${#tex_files[@]}" -eq 0 ]; then
	    echo "No .tex files found."
	    exit 1
	elif [ "${#tex_files[@]}" -eq 1 ]; then
	    # If there is only one .tex file, automatically select it
	    tex_file="${tex_files[0]}"
	else
	    # If there are multiple .tex files, let the user choose one
	    echo "Multiple .tex files found. Please choose one:"
	    select tex_file in "${tex_files[@]}"; do
	        if [ -n "$tex_file" ]; then
	            break
	        else
	            echo "Invalid selection. Please try again."
	        fi
	    done
	fi
}

extract_nth_block() {
    local env_name="$1"
    local nth="$2"
    local file_path="$3"
    local count=0
    local capture=0
    local output=""
    
    while IFS= read -r line; do
        if [[ $line == "\\begin{${env_name}}" ]]; then
            ((count++))
            if [[ $count -eq $nth ]]; then
                capture=1
                output="$line"
            fi
        elif [[ $line == "\\end{${env_name}}" && $capture -eq 1 ]]; then
            output="$output"$'\n'"$line"
            echo "$output"
            return
        elif [[ $capture -eq 1 ]]; then
            output="$output"$'\n'"$line"
        fi
    done < "$file_path"
}

main() {
    local selected_paper=$(cat "$csv_file" | sed '1d' | fzf --delimiter=',' --with-nth=1,2,3,4,5)
    local relative_path=$(echo $selected_paper | cut -d ',' -f 5 | sed 's/"//g')
	echo "$relative_path"

    if [[ -n $selected_paper ]]; then
        local paper_src_path="${pdf_dir}/${relative_path}/src"
        local tex_files=$(find "$paper_src_path" -maxdepth 1 -type f -name '*.tex' | head -n 1)
		choose_from_multiple_tex_files "$tex_files" # This funciton has defined tex_file
		
		nth_block=$(extract_nth_block "equation" 1 "$tex_file")

		echo "$nth_block"

    else
        echo "No paper selected."
    fi
}


main
