#!/usr/bin/env bash

parent_dir="$1"
csv_file="$parent_dir/papers.csv"

selected_paper=$(cat "$csv_file" | sed '1d' | fzf --delimiter=',' --with-nth=1,2,3,4,5)
label=$(echo "$selected_paper" | awk -F',' '{print $5}' )
label=${label:1}        # Remove the first character (")
label=${label%?}        # Remove the last character (")

echo "$label"
