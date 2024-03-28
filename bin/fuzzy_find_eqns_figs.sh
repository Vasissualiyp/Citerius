#!/usr/bin/env bash

parent_dir="$1" # Directory containing reference materials
label="$2"
input_line="$3"

# Configuration variables for paths
csv_file="$parent_dir/papers.csv" # CSV file with metadata for papers
bibtex_file="$parent_dir/bibliography.bib" # BibTeX file with bibliography information
pdf_dir="$parent_dir" # Directory where PDFs are stored

# Determine script directory for relative path operations
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CITERIUS_DIR="$SCRIPT_DIR/.."
BIN_DIR="$SCRIPT_DIR"

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

find_line_by_exact_label() {
    local label="$1"
    local csv_file="$2"
    # Extract the 5th column and find the exact match, then get the line number
    local line_number=$(awk -F',' '{print $5}' "$csv_file" | grep -nxF "\"$label\"" | cut -d: -f1)

    # Adjust line_number to account for any headers you might have skipped
    # For example, if you skipped one header line, you should:
    # line_number=$((line_number + 1))

    if [[ -n $line_number ]]; then
        # Extract the specific line from the csv file
        sed "${line_number}q;d" "$csv_file"
    else
        echo "Label not found."
    fi
}

# Function to handle counting of extra equations in eqnarray environments
treatment_of_extra_eqns() {
    # Check and update matrix environment status
    if [[ $line =~ \\begin\{array\} ]]; then
        in_matrix=true
    elif [[ $line =~ \\end\{array\} ]]; then
        in_matrix=false
    fi

	# Set starred_env_has_label=true if a label is found within a starred environment
    if [[ $in_starred_env == true && $line =~ \\label ]]; then
        starred_env_has_label=true
    fi

    # Process labels as before
    if [[ $line =~ \\label ]]; then
        ((label_count++)) # Increment label count if label is found
    fi

    # Adjusted condition to increment extra count, excluding when in a matrix environment
    if [[ ($current_env == "eqnarray" || $current_env == "align") && $line =~ \\\\ && $in_matrix == false ]]; then
        ((extra_count++)) # Increment extra count if double backslash is found outside of matrix
    fi
}

handle_matrix_environment() {
    # Check for the beginning of a matrix environment
    if [[ $line =~ \\\begin\{array\} ]]; then
        in_matrix=true
    # Check for the end of a matrix environment
    elif [[ $line =~ \\\end\{array\} ]]; then
        in_matrix=false
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
    local end_env_pattern="TEEEEEEEEEST"
    local label_count=0
    local extra_count=0
    local excess_labels=0
    local excess_extra=0
    local total_env_count=0
    local in_env=false
    local current_env=""
    local in_matrix=false
	local in_starred_env=false
    local starred_env_has_label=false
	echo "Set everything up"
    
    # Read file line by line
    while IFS= read -r line; do
        if [[ "$in_env" == false ]]; then
            # Loop through each specified environment name
            for env_name in "${env_names[@]}"; do
                # Check if line marks the beginning of an environment
				if [[ $line =~ ^[[:space:]]*\\begin\{(${env_name})(\*?)\}[[:space:]]*$ ]]; then
						
				    # TREATMENT OF STARRED EQNS BEGINS
				    current_env=${BASH_REMATCH[1]}  # Capture the environment name
				    current_env_starred=${BASH_REMATCH[2]}
				    if [[ $current_env_starred == "*" ]]; then
				        current_env_full="${current_env}\\*"  # Escape the asterisk for regex use
				    else
				        current_env_full="$current_env"
				    fi
				    # Debug print to verify the pattern
				    echo "Start Pattern: $current_env_full"
				    end_env_pattern="^[[:space:]]*\\\\end\\{${current_env_full}\\}[[:space:]]*$"
				    # Debug print to verify the end pattern
				    echo "End Pattern: $end_env_pattern"
				    # TREATMENT OF STARRED EQNS ENDS

				    in_env=true
				    output="$line"
				    label_count=0
				    extra_count=0
				    # Additional logic for starred environments
				    if [[ $line =~ \* ]]; then
				        in_starred_env=true
				    else
				        in_starred_env=false
				    fi
				    break
				fi
            done
        else
            # Append current line to output
            output="$output"$'\n'"$line"
		    # Perform additional processing for labels and extra equations
            treatment_of_extra_eqns
            # Check if line marks the end of the current environment
		    
		    if [[ $line =~ $end_env_pattern ]]; then
				echo "Exit env $env_name"
				# Update counters based on labels and extra equations
				if [[ $in_starred_env == false || ($in_starred_env == true && $starred_env_has_label == true) ]]; then
   				    counting_extra_eqns
   				    ((block_count++))
   				fi
                # Calculate total environment count including excesses
                total_env_count=$((block_count + excess_labels + excess_extra))
                # Check if target count has been reached
                if [[ $total_env_count -ge $target_count ]]; then
				    output=$(echo "$output" | sed '1d')
                    echo "$output"
                    return
                fi
                # Reset state for next environment
                in_env=false
                output=""
				echo "Exited env $env_name"
            fi
        fi
    done < "$file_path"
}

# Function to extract equations using a specified list of environment names.
# It utilizes the extract_environment_with_labels function to find both "equation" and "eqnarray" environments.
extract_equation() {
    echo "Extracting eqn $1 $2"
    extract_environment_with_labels "equation,eqnarray,align" "$1" "$2"
}

# Function to extract figures using the "figure" environment name.
# It calls the extract_environment_with_labels function to specifically find "figure" environments.
extract_figure() {
    echo "Extracting fig $1 $2"
    extract_environment_with_labels "figure" "$1" "$2"
}

# Main function to parse user input for items to find, then extract and print those items from the document.
find_items() {
    local filename="$1" # Filename of the LaTeX document to process
    IFS=' ' read -ra items <<< "$input_line" # Convert the input line into an array of items

    for item in "${items[@]}"; do
        type=${item:0:1} # Extract the first character to determine the type (figure or equation)
        number=${item:1} # Extract the rest of the string as the item number

        case $type in
            f)
                #echo "Extracting figure $number:" # Notify user about the figure being extracted
                extract_figure "$number" "$filename" # Call extract_figure function with the number and filename
                ;;
            e)
                #echo "Extracting equation $number:" # Notify user about the equation being extracted
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
	local selected_paper=$(find_line_by_exact_label "$label" "$csv_file")
    # Extract the relative path from the selected paper's data
    local relative_path=$(echo $selected_paper | cut -d ',' -f 5 | sed 's/"//g')
    #echo "$relative_path"

    # Proceed if a paper has been selected
    if [[ -n $selected_paper ]]; then
        # Construct the source path for the paper's LaTeX files
        local paper_src_path="${pdf_dir}/${relative_path}/src"
        # Find .tex files within the source path
        local tex_files=$(find "$paper_src_path" -maxdepth 1 -type f -name '*.tex' | head -n 1)
        choose_from_multiple_tex_files "$tex_files" # Allow user to choose a .tex file if multiple are found
        
        # Call find_items to process user input and extract requested items from the chosen .tex file
        find_items "$tex_file"
    else
        echo "No paper selected." # Inform user if no paper was selected
    fi
}

# Call the main function to start the script
main
