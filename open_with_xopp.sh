#!/usr/bin/env bash

# Configuration variables
parent_dir="$HOME/research/references"
csv_file="$parent_dir/papers.csv"
bibtex_file="$parent_dir/bibliography.bib"
pdf_dir="$parent_dir/$1"

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

create_xopp_from_pdf() {
  xopp_file_path="$1"
  filename="$2"
  xournalpp "$filename" &
  
  # Wait for Xournal++ to launch
  sleep 0.5
  
  # Use xdotool to simulate Ctrl+S to save
  xdotool key "ctrl+s"
  
  # Wait for the save dialog to appear
  sleep 0.5
  
  # Type the path to save the file and press Enter
  xdotool type "$xopp_file_path"
  xdotool key "Return"
}
run_inkscape_tablet_daemon

# Extract the filename without the extension
filename="$1.pdf"
filename_no_ext="${filename%.pdf}"

cd "$pdf_dir"

# Open the PDF in Xournal++
xopp_file_path="$pdf_dir/$filename_no_ext.xopp"
if [ -f "$xopp_file_path" ]; then
  xournalpp "$xopp_file_path" &
else
  create_xopp_from_pdf "$xopp_file_path" "$filename"
fi
