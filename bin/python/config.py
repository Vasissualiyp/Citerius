import pandas as pd
from pyfzf import FzfPrompt
import tempfile
import shutil
import os
import sys
import re

def find_bibtex_entry(content, label):
    """
    Obtains bibtex entry from a list of lines, corresponding to bibtex file
    Args:
        content (list of str): bibtex file, separated into list of lines
        (how it's being read by readlines())
        label (str): label of entry of interest

    Returns:
        str: multiline string, bibtex entry for label of interest. 
        returns None if bibtex entry for given label wasn't found.
    """
    # Escape special characters in the label to prevent regex issues
    escaped_label = re.escape(label)
    # Construct the regex pattern
    pattern = r'@[a-z]+\{%s\s*,.*?^\s*\}' % escaped_label
    # Compile with flags to handle multiline entries
    regex = re.compile(pattern, flags=re.DOTALL | re.MULTILINE)
    # Search for the pattern in the content
    content_str = ""
    for line in content:
        content_str += line
    match = regex.search(content_str)
    return match.group(0) if match else None

def remove_multiline_block(file_path, start_pattern, end_pattern):
    # Create a temporary file to write the cleaned content
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        with open(file_path, 'r') as original_file:
            in_block = False  # Track whether we're inside the block to remove
            for line in original_file:
                if re.match(start_pattern, line):
                    in_block = True  # Block starts here
                if not in_block:
                    temp_file.write(line)  # Write lines outside the block
                if in_block and re.search(end_pattern, line):
                    in_block = False  # Block ends here (skip closing line)
        # Replace the original file with the temporary file
        os.replace(temp_file.name, file_path)


def remove_ith_line(filename, i):
    temp_filename = f"{filename}.tmp"
    line_count = 0

    with open(filename, 'r') as infile, open(temp_filename, 'w') as outfile:
        for line in infile:
            if line_count != i:
                outfile.write(line)
            line_count += 1

    # Replace the original file with the temporary file
    os.replace(temp_filename, filename)

class CiteriusConfig():
    def __init__(self, ref_dir: str):
        """
        Citerius config class. 
        Args:
            ref_dir (str): path to directory with references
        """
        # Set up paths
        self.parent_dir = ref_dir
        self.csv_file = os.path.join(ref_dir, 'papers.csv')
        self.bibtex_file = os.path.join(ref_dir, 'bibliography.bib')
        self.df_loaded = False

    def load_df(self):
        """
        Loads dataframe of all the papers. 
        Required to do anything with it.
        """
        self.df = pd.read_csv(self.csv_file)
        self.df_columns = self.df.columns.tolist()
        self.df_loaded = True

    def fuzzy_find_label(self):
        """
        Performs fuzzy find over the database of all the papers,
        and returns the label of the requested paper
        """
        if not self.df_loaded:
            self.load_df()
        list_of_lines = []
        concat_str = ", "
        for i in range(len(self.df)):
            line = ""
            for column in self.df_columns:
                line = line + concat_str + str(self.df[column][i])
            line = line[len(concat_str):] # remove leading ', ' string
            list_of_lines.append(line)

        fzf = FzfPrompt()
        chosen_line = fzf.prompt(list_of_lines)
        if len(chosen_line) == 0:
            print("Fuzzy find failed - no papers found.")
            exit(0)
        line_idx = list_of_lines.index(chosen_line[0])

        label = self.df['Label'][line_idx]
        return label

    def remove_paper(self, label: str):
        """
        Removes mentions of paper of provided label from csv, bib files, 
        as well as its directory
        """
        labels_column = self.df['Label'].tolist()
        label_idx = labels_column.index(label)
        
        # Remove csv entry
        remove_ith_line(self.csv_file, label_idx + 1)

        # Remove bibtex entry
        escaped_label = re.escape(label)
        start_pattern = re.compile(r'^@[a-z]+\{%s\s*,' % escaped_label)  # Match "@article{<label>,"
        end_pattern = re.compile(r'^\s*}\s*$\s*$')  # Match a line with only "}"
        remove_multiline_block(self.bibtex_file, start_pattern, end_pattern)
        
        # Remove directory with paper pdf and its src if needed
        paper_dir = os.path.join(self.parent_dir, label)
        try:
            shutil.rmtree(paper_dir)
        except:
            print("Directory with the paper's pdf doesn't exist")


if __name__ == "__main__":
    ref_dir = sys.argv[1]
    #ref_dir = "/home/vasilii/research/references"
    citerius = CiteriusConfig(ref_dir)
    label = citerius.fuzzy_find_label()
    label = "FirstStars"
    print(label)
