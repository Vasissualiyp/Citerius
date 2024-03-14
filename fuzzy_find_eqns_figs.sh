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

extract_environment_with_labels() {
    IFS=',' read -r -a env_names <<< "$1"
    local target_count="$2"
    local file_path="$3"
    
    local block_count=0
    local output=""
    local label_count=0
    local excess_labels=0
    local total_env_count=0
    local in_env=false
    local current_env=""
    
    while IFS= read -r line; do
        if [[ "$in_env" == false ]]; then
            for env_name in "${env_names[@]}"; do
                if [[ $line =~ ^[[:space:]]*\\begin\{${env_name}\}[[:space:]]*$ ]]; then
                    in_env=true
                    current_env=$env_name
                    output="$line"
                    label_count=0
                    break
                fi
            done
        else
            output="$output"$'\n'"$line"
            if [[ $line =~ \\label ]]; then
                ((label_count++))
            fi
            if [[ $line =~ ^[[:space:]]*\\end\{${current_env}\}[[:space:]]*$ ]]; then
                if [[ $label_count -gt 1 ]]; then
                    ((excess_labels+=label_count-1))
                fi
                ((block_count++))
                total_env_count=$((block_count + excess_labels))
                if [[ $total_env_count -ge $target_count ]]; then
                    echo "$output"
                    return
                fi
                in_env=false
                output=""
            fi
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
		
		nth_block=$(extract_environment_with_labels "equation,eqnarray" 4 "$tex_file")

		echo "$nth_block"

    else
        echo "No paper selected."
    fi
}


main
