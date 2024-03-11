#!/usr/bin/env bash

# Configuration variables
parent_dir="$HOME/research/references"
csv_file="$parent_dir/papers.csv"
bibtex_file="$parent_dir/bibliography.bib"
pdf_dir="$parent_dir"

# Check if an argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <pdf_file>"
    exit 1
fi

# Run the tablet regulator script for inkscape
run_inkscape_tablet_daemon() {
  if pgrep -f "tablet_regulator" > /dev/null; then
    echo "inkscape_tablet_regulator is already running"
  else
    echo "The script is not running. Starting the script."
    nohup "$HOME/scripts/inkscape_tablet_regulator.sh" > /dev/null &
  fi
}

run_inkscape_tablet_daemon

# Extract the filename without the extension
filename=$(basename -- "$1")
filename_no_ext="${filename%.pdf}"

cd "$paper_dir"

# Open the PDF in Xournal++
xournalpp "$filename" &

# Wait for Xournal++ to launch
sleep 1

# Use xdotool to simulate Ctrl+S to save
xdotool key "ctrl+s"

# Wait for the save dialog to appear
sleep 1

# Type the path to save the file and press Enter
xopp_file_path="$paper_dir/$filename_no_ext.xopp"
xdotool type "$xopp_file_path"
xdotool key "Return"
