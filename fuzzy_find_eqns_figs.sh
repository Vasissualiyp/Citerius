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
    local env_name="$1"
    local target_count="$2"
    local file_path="$3"
    
    local count=0
    local excess_label=0
    local block_count=0
    local in_block=0
    local output=""
    local label_count=0

    while IFS= read -r line; do
        # Enter environment block
        if [[ $line =~ ^[[:space:]]*\\begin\{${env_name}\}[[:space:]]*$ ]]; then
            if [[ $in_block -eq 1 ]]; then
                # If nested environment, reset but typically should not happen in well-formed LaTeX for equation/figure
                label_count=0
            fi
            in_block=1
            output="$line"
            continue
        fi

        # Exit environment block
        if [[ $line =~ ^[[:space:]]*\\end\{${env_name}\}[[:space:]]*$ && $in_block -eq 1 ]]; then
            output="$output"$'\n'"$line"
            in_block=0
            # Calculate total environments including those implied by excess labels
            if [ $label_count -gt 1 ]; then
                ((excess_label+=label_count-1))
            fi
            ((block_count++))
            label_count=0

            # Determine if the current count meets the user's criteria
            if [ $((block_count + excess_label)) -ge $target_count ]; then
                echo "$output"
                return
            else
                output=""
            fi
        elif [[ $in_block -eq 1 ]]; then
            # Count labels and accumulate output only within environment blocks
            [[ $line =~ \\label ]] && ((label_count++))
            output="$output"$'\n'"$line"
        fi
    done < "$file_path"
}

# Example usage
# extract_environment_with_labels "equation" 2 "your_file.tex"

main() {
    local selected_paper=$(cat "$csv_file" | sed '1d' | fzf --delimiter=',' --with-nth=1,2,3,4,5)
    local relative_path=$(echo $selected_paper | cut -d ',' -f 5 | sed 's/"//g')
	echo "$relative_path"

    if [[ -n $selected_paper ]]; then
        local paper_src_path="${pdf_dir}/${relative_path}/src"
        local tex_files=$(find "$paper_src_path" -maxdepth 1 -type f -name '*.tex' | head -n 1)
		choose_from_multiple_tex_files "$tex_files" # This funciton has defined tex_file
		
		nth_block=$(extract_environment_with_labels "equation" 4 "$tex_file")

		echo "$nth_block"

    else
        echo "No paper selected."
    fi
}


main
