import pandas as pd
from pyfzf import FzfPrompt
import os
import sys

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
        for i in range(len(self.df)):
            line = ""
            for column in self.df_columns:
                line = line + ", " + str(self.df[column][i])
            line = line[2:] # remove leading ', ' string
            list_of_lines.append(line)

        fzf = FzfPrompt()
        chosen_line = fzf.prompt(list_of_lines)
        if len(chosen_line) == 0:
            print("Fuzzy find failed - no papers found.")
            exit(0)
        line_idx = list_of_lines.index(chosen_line[0])

        label = self.df['Label'][line_idx]
        return label

if __name__ == "__main__":
    ref_dir = sys.argv[1]
    #ref_dir = "/home/vasilii/research/references"
    citerius = CiteriusConfig(ref_dir)
    label = citerius.fuzzy_find_label()
    print(label)
