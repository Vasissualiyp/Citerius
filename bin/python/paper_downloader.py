import pybtex as pbt
from config import CiteriusConfig
from pathlib import Path
from urllib.request import urlretrieve
from utils import CiteriusUtils
import os
import re
import sys
import arxiv
import tarfile

class PaperDownloader():

    def __init__(self, config_file, 
                 download_id: str, 
                 first_time_download = True, 
                 no_commits = False):
        """
        Class to set up and download the paper from its arxiv id.
        Args:
            config_file (str): path to json config file 
                (if None, then the default value is $HOME/user/.config/citerius/config.json)
            download_id (str): 
                id of paper on arxv to download, OR
                download link, OR
                label for paper to be downloaded via Citerius dataframe
            first_time_download (bool): whether we're downloading a paper that 
                was in the database before
            no_commits (bool): set to true if don't want to commit changes 
                (in case downloading in bulk, for instance)
        """

        self.citerius = CiteriusConfig(config_file)
        self.cutils = CiteriusUtils()
        self.first_time_download = first_time_download
        self.no_commits = no_commits

        if self.first_time_download:
            self.arxiv_id, self.download_link = self.cutils.check_if_string_is_arxiv_id(download_id)
            if self.download_link == 'nan': # Arxiv paper
                self.citation_str = self.cutils.get_citation_from_arxiv_id(self.arxiv_id)
            else: # Paper with link to download
                editor = "vim"
                self.get_citation_from_tmpfile(editor)
            self.get_arxiv_paper_info()

        else:
            self.get_paper_info_from_citerius_df(download_id)

    def get_paper_info_from_citerius_df(self, label):

        # Obtain database entry, related to paper
        self.citerius.load_df()
        df_row = self.citerius.df[self.citerius.df.Label == label]
        if df_row.empty:
            raise ValueError(f"No label {label} found in the dataframe!")

        self.full_authors     = df_row.Author.iloc[0]
        self.full_title       = df_row.Title.iloc[0]
        self.year             = df_row.Year.iloc[0]
        self.arxiv_id         = str(df_row["ArXiv Number"].iloc[0])
        self.default_label    = df_row.Label.iloc[0]
        self.label            = df_row.Label.iloc[0]
        self.download_ans     = df_row.Download_pdf.iloc[0]
        self.download_src_ans = df_row.Download_src.iloc[0]
        self.download_link    = df_row.Download_link.iloc[0]

    def replace_label_for_citation(self):
        """
        Replases the label for citation string with value in self.label
        """
        if self.download_link == 'nan':
            self.citation_str = self.citation_str.replace(self.arxiv_id, self.label, 1)
        elif self.arxiv_id == 'nan':
            init_label = self.cutils.obtain_label_from_bibentry(self.citation_str)
            self.citation_str = self.citation_str.replace(init_label, self.label, 1)

    def get_arxiv_paper_info(self):
        """
        Obtains a bunch of paper information from citation string, obtained before
        """
    
        concat_string = " and " 

        if self.citation_str == None:
            print("There was an error when obtaining citation string")
            exit(1)
        
        # Extract bibliography data from citation string
        bibdata = pbt.database.parse_string(self.citation_str, "bibtex").entries[self.arxiv_id]
        
        self.full_title = bibdata.fields['title']
        self.year = bibdata.fields['year']
        full_author_list = bibdata.persons['author']
        full_author_str = ""
        for author in full_author_list:
            author_str = str(author)
            lastname =  str(author_str.split()[0])
            firstname = str(author_str.split()[1])
            lastname_alpha = ''.join(char for char in lastname if char.isalpha())
            firstname_alpha = ''.join(char for char in firstname if char.isalpha())
            full_author_str += concat_string + lastname_alpha + " " + firstname_alpha[0]
        self.full_authors = full_author_str[len(concat_string):]
    
        # Create default label
        first_author = full_author_list[0]
        first_author_lastname = str(first_author).split()[1].strip()
        first_word_title = str(self.full_title).split()[0].strip()
        first_word_title_alpha = ''.join(char for char in first_word_title if char.isalpha())
        self.default_label = first_author_lastname + first_word_title_alpha + self.year

    # New paper download functions

    def setup_download_paths(self):
        """
        Sets up relevant paths for downloading of the paper or its source
        """
        self.download_dir = os.path.join(self.citerius.parent_dir, self.label)
        self.download_name = self.label + '.pdf'
        self.download_path = os.path.join(self.download_dir, self.download_name)

        self.download_src_dir = os.path.join(self.download_dir, "src")
        self.download_src_name = self.label + '.tar.gz'
        self.download_src_path = os.path.join(self.download_src_dir, self.download_src_name)

    def append_bibtex(self):
        """
        Appends bibtex entry to the bibliography file,
        as well as this paper's string to csv file
        """
    
        csv_str = f"\"{self.full_title}\",\"{self.full_authors}\",\"{self.arxiv_id}\",\"{self.year}\",\"{self.label}\",\"{self.download_ans}\",\"{self.download_src_ans}\",\"{self.download_link}\"\n"
    
        csv_file = open(self.citerius.csv_file, "a")
        csv_file.write(csv_str)
        csv_file.close()
    
        bib_file = open(self.citerius.bibtex_file, "a")
        bib_file.write(self.citation_str)
        bib_file.close()

    def create_dirs(self):
        """
        Creates directories for downloading of the paper and 
        appends paper info to bibtex, csv files
        """
        try:
            os.mkdir(self.download_dir)
            if self.first_time_download: self.append_bibtex()
        except:
            print(f"There is already a paper with the label {self.label}")
            if self.download_src_ans == 'y':
                # Here need to implement changing of csv file to change "download_src" column
                pass

        if self.download_src_ans == 'y':
            try:
                os.mkdir(self.download_src_dir)
            except:
                print(f"There is already source for a paper with the label {self.label}")
    
    # Prompt user for input

    def prompt_for_download(self):
        """
        Prompts for the user before downloading of the paper
        """
        print(f"The paper title is: {self.full_title}\n")
        print(f"The paper author(s) are: {self.full_authors}\n")

        download_ans = self.input_with_default("Would you life to download this paper? (Y/n): ", "y")
        
        if self.download_link == "nan":
            download_src_ans = self.input_with_default("Would you life to download the source for this paper? (y/N): ", "n")
        else:
            download_src_ans = 'n'
        
        if (download_ans.lower() == 'n' and download_src_ans.lower() == 'n'):
            print("No download will happen. Exiting...")
            label = "nan"
            exit(0)
        else:
            label = input("What would be the paper's label? (leave empty for default): ")
            if label == "":
                label = self.default_label
    
        self.download_ans = download_ans.lower()
        self.download_src_ans = download_src_ans.lower()
        self.label = label

    def overwrite_prompt(self):
        """
        Treatment of overwriting of paper pdf via prompting the user
        """
        if Path(self.download_path).exists() and self.download_ans == 'y':
            overwrite = self.input_with_default(f"The pdf of paper with label {self.label} was already downloaded. Overwrite? (y/N)", 'n')
        else:
            overwrite = 'n'
        
        if overwrite == 'n' and Path(self.download_path).exists(): self.download_ans = 'n'

    def input_with_default(self, prompt: str, default: str):
        """
        Calls for user input. If no answer provided, will default to given value

        Args:
            prompt (str): prompt for input
            default (str): default value for input

        Returns:
            str: user-provided input
        """
        num_attempts = 5
        valid_inputs = [ 'y', 'n' ]
        while num_attempts > 0:
            usr_input = input(prompt)
            if usr_input == "":
                usr_input = default
            if usr_input.lower() in valid_inputs:
                return usr_input.lower()
            else:
                print(f"Invalid user input: {usr_input}. Allowed values: {valid_inputs}. Please, try again.")
                num_attempts -= 1
        raise TimeoutError("Too many wrong attempts")

    def get_citation_from_tmpfile(self, editor: str):
        """
        Function to prompt user to insert biiliography
        info into temporary file, which it then reads and
        extracts relevant data from
        """
        initial_content_str = '''
% Please, paste the bibliography file here.
% All lines starting with '%' will be ignored.
% You can also uncomment and edit the sample 
% minimal bibliography entry below:
%@unpublished{label,
%    author = "Doe, John and Last, First",
%    title = "Title",
%    year = "2000"
%}
'''
        content = self.cutils.get_user_input_via_editor(initial_content_str, editor)
        # Remove lines starting with % and empty lines
        if content == None:
            print("No bibliography info was provided. Exiting...")
            exit(0)
        lines = [ 
            line for line in content.split('\n')
            if line.strip() != '' and not line.lstrip().startswith('%')
        ]
        content_nocomments = '\n'.join(lines)
        self.citation_str = content_nocomments
        if self.citation_str == "":
            self.citation_str = None
        
    # Main download externally-called funcitons

    def download_paper_with_user_input(self):
        """
        Downloads the paper with required user input
        """
        self.prompt_for_download()
        
        # Change the paper's label in its bibtex citation
        self.replace_label_for_citation()
        self.setup_download_paths()
        self.create_dirs()

        self.overwrite_prompt()
        self.download_paper_general()

    def download_paper_without_user_input(self, 
                                          download_paper='y',
                                          download_src='n',
                                          label="",
                                          overwrite='n'):
        """
        Downloads the paper without user input, by passing answers directly instead
        """
        self.download_ans = download_paper.lower()
        self.download_src_ans = download_src.lower()
        if label == "":
            self.label = self.default_label
        else:
            self.label = label
        
        # Change the paper's label in its bibtex citation
        self.replace_label_for_citation()
        self.setup_download_paths()
        self.create_dirs()

        if overwrite == 'n' and Path(self.download_path).exists(): self.download_ans = 'n'
        self.download_paper_general()

    def download_paper_from_citerius_df(self):
        """
        Downloads paper from its info in citerius dataframe
        """
        if self.first_time_download:
            raise ValueError(f"In order to download from Citerius dataframe, please set up PaperDownloader class with first_time_download=False!")
        self.setup_download_paths()
        self.create_dirs()
        if Path(self.download_path).exists(): 
            self.download_ans = 'n'
        self.download_paper_general()

    # Download from sources

    def download_paper_general(self):
        """
        General function to identify the method for paper download and download the paper itself
        """
        if str(self.download_link).lower() == 'nan':
            self.download_arxiv_paper()
        elif str(self.arxiv_id).lower() == 'nan':
            self.download_paper_from_link()
        elif (self.download_ans == 'n' and self.download_src_ans == 'n'):
            print(f"The paper {self.label} is a part of git repository, thus doesn't require download")
            return
        else:
            print("Unknown situation with arxiv_id and download_link both not being nan.")
            print(f"arxiv_id: {self.arxiv_id}")
            print(f"download_link: {self.download_link}")
            exit(1)

        if self.first_time_download and not self.no_commits:
            commit_message = f"Added paper with label {self.label}"
            self.citerius.git_update_files(commit_message)

    def download_arxiv_paper(self):
        """
        Downloads paper or its source from arxiv
        """
        if (self.download_ans == 'y') or (self.download_src_ans == 'y'):
            paper = next(arxiv.Client().results(arxiv.Search(id_list=[self.arxiv_id])))
        
        if (self.download_ans == 'y'):
            print(f"Will start downloading the paper {self.label}")
            paper.download_pdf(dirpath=self.download_dir, 
                               filename=self.download_name)
            print("Done!")
        if (self.download_src_ans == 'y'):
            print(f"Will start downloading source ofthe paper {self.label}")
            paper.download_source(dirpath=self.download_src_dir, 
                                  filename=self.download_src_name)
            print("Download done! Uncompressing the .tar file...")
            file = tarfile.open(self.download_src_path)
            file.extractall(self.download_src_dir)
            file.close()
            os.remove(self.download_src_path)
            print("Done!")

    def download_paper_from_link(self):
        """
        Downloads the paper from a provided link, not from arxiv
        """
        if (self.download_ans == 'y'):
            print(f"Will start downloading the paper {self.label}")
            urlretrieve(self.download_link, self.download_path)
            print("Done!")

class BulkDownloader():
    def __init__(self, config_file=None, download_mode="new"):
        """
        Download a bunch of papers at once
        Args:
            config_file (str): path to json config file 
                (if None, then the default value is $HOME/user/.config/citerius/config.json)
            download_mode (str): how the papers will be downloaded
        """
        self.citerius = CiteriusConfig(config_file)
        self.ref_dir = self.citerius.parent_dir
        self.config_file = config_file

        if download_mode == "new":
            self.download_params = ['y', 'n', "", 'n']
        elif download_mode == "old":
            self.download_params = ['y', 'n', "", 'n']
        else:
            raise ValueError(f"Unknown value for download_mode: {download_mode}")

    def download_from_list(self, list, first_time_download=True):
        """
        Download papers from python list, either with Citerius, or with 
        general download without user intervention
        """
        concat_string = ", "
        labels_str = ""
        for download_id in list:
            paper_download = PaperDownloader(self.config_file, download_id, 
                                             first_time_download, no_commits=True)
            if first_time_download:
                paper_download.download_paper_without_user_input(*self.download_params)
                labels_str+= concat_string + paper_download.label
            else:
                paper_download.download_paper_from_citerius_df()

        if first_time_download:
            labels_str = labels_str[len(concat_string):]
            commit_message = f"Added papers with labels: {labels_str}"
            self.citerius.git_update_files(commit_message)

    def download_from_citerius(self):
        """
        Downloads all papers from Citerius dataframe
        """
        self.citerius.load_df()
        labels_list = self.citerius.df.Label.tolist()
        self.download_from_list(labels_list, first_time_download=False)

    def download_from_file(self, file_path):
        """
        Downloads papers from file
        """
        # Get a list of papers from the file
        file = open(file_path, 'r')
        arxiv_ids = []
        for line in file:
            arxiv_ids.append(line.strip())
        file.close()

        self.download_from_list(arxiv_ids)
