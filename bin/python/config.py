import pandas as pd
import pybtex
from pyfzf import FzfPrompt
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
        
        csv = open(self.csv_file)
        content = csv.readlines()
        print(content[label_idx+1])

        bib = open(self.bibtex_file)
        content = bib.readlines()
        matches = find_bibtex_entry(content, label)
        print(matches)

if __name__ == "__main__":
    ref_dir = sys.argv[1]
    #ref_dir = "/home/vasilii/research/references"
    citerius = CiteriusConfig(ref_dir)
    #label = citerius.fuzzy_find_label()
    label = "FirstStars"
    print(label)
    citerius.load_df()
    citerius.remove_paper(label)
