import pandas as pd
from pyfzf import FzfPrompt
import os

class CiteriusConfig():
    def __init__(self, ref_dir: str):
        """
        Citerius config class. 
        Args:
            ref_dir (str) - path to directory with references
        """
        # Set up paths
        self.parent_dir = ref_dir
        self.csv_file = os.path.join(ref_dir, 'papers.csv')
        self.bibtex_file = os.path.join(ref_dir, 'bibliography.bib')

        # Create pandas dataframe
        self.df = pd.read_csv(self.csv_file)
        self.df_columns = self.df.columns.tolist()
        self.label_column_idx = self.df_columns.index("Label")

    def fuzzy_find_label(self):
        """
        Performs fuzzy find over the database of all the papers,
        and returns the label of the requested paper
        """
        list_of_lines = []
        for i in range(len(self.df)):
            line = ""
            for column in self.df_columns:
                line = line + ", " + str(self.df[column][i])
            line = line[2:] # remove leading ', ' string
            list_of_lines.append(line)

        fzf = FzfPrompt()
        chosen_line = fzf.prompt(list_of_lines)[0]
        line_idx = list_of_lines.index(chosen_line)

        label = self.df['Label'][line_idx]
        return label

if __name__ == "__main__":
    ref_dir = "/home/vasilii/research/references"
    citerius = CiteriusConfig(ref_dir)
    label = citerius.fuzzy_find_label()
    print(f"Line label: {label}")
