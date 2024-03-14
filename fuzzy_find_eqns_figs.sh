#!/usr/bin/env bash

# Configuration variables for paths
parent_dir="$HOME/research/references" # Directory containing reference materials
csv_file="$parent_dir/papers.csv" # CSV file with metadata for papers
bibtex_file="$parent_dir/bibliography.bib" # BibTeX file with bibliography information
pdf_dir="$parent_dir" # Directory where PDFs are stored

# Determine script directory for relative path operations
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CITERIUS_DIR="$SCRIPT_DIR"

# Function to handle the selection of a .tex file when multiple are present
choose_from_multiple_tex_files() {
	if [ "${#tex_files[@]}" -eq 0 ]; then
	    echo "No .tex files found." # No files found case
	    exit 1
	elif [ "${#tex_files[@]}" -eq 1 ]; then
	    # Auto-select the single found .tex file
	    tex_file="${tex_files[0]}"
	else
	    # Prompt user to choose from multiple .tex files
	    echo "Multiple .tex files found. Please choose one:"
	    select tex_file in "${tex_files[@]}"; do
	        if [ -n "$tex_file" ]; then
	            break # Exit loop after selection
	        else
	            echo "Invalid selection. Please try again."
	        fi
	    done
	fi
}

# Function to handle counting of extra equations in eqnarray environments
treatment_of_extra_eqns() {
    if [[ $line =~ \\label ]]; then
        ((label_count++)) # Increment label count if label is found
    fi
    if [[ $current_env == "eqnarray" ]] && [[ $line =~ \\\\ ]]; then
        ((extra_count++)) # Increment extra count if double backslash is found in eqnarray
    fi
}

# Function to update counters based on the collected data
counting_extra_eqns() {
    if [[ $label_count -gt 1 ]]; then
        ((excess_labels+=label_count-1)) # Calculate excess labels
    fi
    if [[ $extra_count -gt 0 ]]; then
        ((excess_extra+=extra_count)) # Update excess extra count
    fi
}

# Main function to extract environments with labels from LaTeX documents
extract_environment_with_labels() {
    # Split input string into array based on comma delimiter
    IFS=',' read -r -a env_names <<< "$1"
    local target_count="$2" # Target count for item extraction
    local file_path="$3" # Path to the LaTeX document
    
    # Initialize counters and state variables
    local block_count=0
    local output=""
    local label_count=0
    local extra_count=0
    local excess_labels=0
    local excess_extra=0
    local total_env_count=0
    local in_env=false
    local current_env=""
    
    # Read file line by line
    while IFS= read -r line; do
        if [[ "$in_env" == false ]]; then
            # Loop through each specified environment name
            for env_name in "${env_names[@]}"; do
                # Check if line marks the beginning of an environment
                if [[ $line =~ ^[[:space:]]*\\begin\{${env_name}\}[[:space:]]*$ ]]; then
                    in_env=true
                    current_env=$env_name
                    output="$line"
                    label_count=0
                    extra_count=0
                    break # Exit loop on first match
                fi
            done
        else
            # Append current line to output
            output="$output"$'\n'"$line"
		    # Perform additional processing for labels and extra equations
            treatment_of_extra_eqns
            # Check if line marks the end of the current environment
            if [[ $line =~ ^[[:space:]]*\\end\{${current_env}\}[[:space:]]*$ ]]; then
				# Update counters based on labels and extra equations
                counting_extra_eqns
                ((block_count++))
                # Calculate total environment count including excesses
                total_env_count=$((block_count + excess_labels + excess_extra))
                # Check if target count has been reached
                if [[ $total_env_count -ge $target_count ]]; then
                    echo "$output"
                    return
                fi
                # Reset state for next environment
                in_env=false
                output=""
            fi
        fi
    done < "$file_path"
}

# Function to extract equations using a specified list of environment names.
# It utilizes the extract_environment_with_labels function to find both "equation" and "eqnarray" environments.
extract_equation() {
    extract_environment_with_labels "equation,eqnarray" "$1" "$2"
}

# Function to extract figures using the "figure" environment name.
# It calls the extract_environment_with_labels function to specifically find "figure" environments.
extract_figure() {
    extract_environment_with_labels "figure" "$1" "$2"
}

# Main function to parse user input for items to find, then extract and print those items from the document.
find_items() {
    local filename="$1" # Filename of the LaTeX document to process
    echo "LEGEND: f for figures, e for equations, followed by the number of item"
    read -p "Enter the items you want to find (e.g., 'f5 e12' for 5th figure and 12th equation): " input_line
    IFS=' ' read -ra items <<< "$input_line" # Convert the input line into an array of items

    for item in "${items[@]}"; do
        type=${item:0:1} # Extract the first character to determine the type (figure or equation)
        number=${item:1} # Extract the rest of the string as the item number

        case $type in
            f)
                echo "Extracting figure $number:" # Notify user about the figure being extracted
                extract_figure "$number" "$filename" # Call extract_figure function with the number and filename
                ;;
            e)
                echo "Extracting equation $number:" # Notify user about the equation being extracted
                extract_equation "$number" "$filename" # Call extract_equation function with the number and filename
                ;;
            *)
                echo "Unknown item type: $type" # Handle case of unknown item type
                ;;
        esac
    done
}

# The main logic of the script, orchestrating the selection of a paper and extraction of specified items.
main() {
    # Use fzf to select a paper from the CSV file, ignoring the header line
    local selected_paper=$(cat "$csv_file" | sed '1d' | fzf --delimiter=',' --with-nth=1,2,3,4,5)
    # Extract the relative path from the selected paper's data
    local relative_path=$(echo $selected_paper | cut -d ',' -f 5 | sed 's/"//g')
    echo "$relative_path"

    # Proceed if a paper has been selected
    if [[ -n $selected_paper ]]; then
        # Construct the source path for the paper's LaTeX files
        local paper_src_path="${pdf_dir}/${relative_path}/src"
        # Find .tex files within the source path
        local tex_files=$(find "$paper_src_path" -maxdepth 1 -type f -name '*.tex' | head -n 1)
        choose_from_multiple_tex_files "$tex_files" # Allow user to choose a .tex file if multiple are found
        
        # Call find_items to process user input and extract requested items from the chosen .tex file
        find_items "$tex_file"

        # Uncommented nth_block variable assignment was likely meant for debugging or specific extraction purposes
        # nth_block=$(extract_environment_with_labels "equation,eqnarray" 4 "$tex_file")
        # echo "$nth_block"

    else
        echo "No paper selected." # Inform user if no paper was selected
    fi
}

# Call the main function to start the script
main
