import pandas as pd
from pyfzf import FzfPrompt
from pathlib import Path
from utils import CiteriusUtils
from git import Repo, Actor
import shutil
import os
import sys
import re
import json

class CiteriusConfig():
    def __init__(self, config_file=None):
        """
        Citerius config class. 
        Args:
            config_file (str): path to json config file 
                (if None, then the default value is $HOME/user/.config/citerius/config.json)
        """
        if config_file==None:
            self.config_file = os.path.join(Path.home(), ".config/citerius/config.json")
        else:
            self.config_file = config_file
        self.extract_data_from_config_file()
        self.cutils = CiteriusUtils()
        self.df_loaded = False

    def extract_data_from_config_file(self):
        """
        Extract json data from config file and assign corresponding variables 
        in this class.
        """
        with open(self.config_file) as f:
            json_str = f.read()
        config = json.loads(json_str)

        self.parent_dir = config["references_dir"]
        author_name = config["author_name"]
        author_email = config["author_email"]

        self.csv_file = os.path.join(self.parent_dir, 'papers.csv')
        self.bibtex_file = os.path.join(self.parent_dir, 'bibliography.bib')
        self.repo = Repo(self.parent_dir)
        self.author = Actor(author_name, author_email)

    def load_df(self):
        """
        Loads dataframe of all the papers. 
        Required to do anything with it.
        """
        self.df = pd.read_csv(self.csv_file)
        self.df_columns = self.df.columns.tolist()

        # Remove columns that provide no useful info for fzf
        irrelevant_columns = [ "Download_pdf", "Download_link", "Download_src" ]
        for col in irrelevant_columns:
            self.df_columns.remove(col)

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
        labels_column = self.df.Label.tolist()
        label_idx = labels_column.index(label)
        
        # Remove csv entry
        self.cutils.remove_ith_line(self.csv_file, label_idx + 1)

        # Remove bibtex entry
        escaped_label = re.escape(label)
        start_pattern = re.compile(r'^@[a-z]+\{%s\s*,' % escaped_label)  # Match "@article{<label>,"
        end_pattern = re.compile(r'^\s*}\s*$\s*$')  # Match a line with only "}"
        self.cutils.remove_multiline_block(self.bibtex_file, start_pattern, end_pattern)
        
        # Remove directory with paper pdf and its src if needed
        paper_dir = os.path.join(self.parent_dir, label)
        try:
            shutil.rmtree(paper_dir)
        except:
            print("Directory with the paper's pdf doesn't exist")
        finally:
            commit_message = f"Removed paper with label {label}"
            self.git_update_files(commit_message)

    def git_update_files(self, commit_message: str):
        """
        Updates all necessary files and commits with a provided message
        """
        index = self.repo.index
        index.add([self.csv_file, self.bibtex_file])
        index.add([self.csv_file, self.bibtex_file])
        index.commit(commit_message, author=self.author, committer=self.author)

if __name__ == "__main__":
    #ref_dir = sys.argv[1]
    config_file = None # default location for the config file
    citerius = CiteriusConfig(config_file)
    label = citerius.fuzzy_find_label()
    print(label)
    citerius.repo.close()
    #citerius.remove_paper(label)
