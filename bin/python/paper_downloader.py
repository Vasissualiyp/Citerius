import pybibget as pbg
import pybtex as pbt
from config import CiteriusConfig
from pathlib import Path
from urllib.request import urlretrieve
import os
import re
import sys
import asyncio
import arxiv
import tarfile
import tempfile
import subprocess

class CiteriusUtils():
    def get_user_input_via_editor(self, initial_content="", editor=None):
        # Determine the editor to use (defaults to vim or $EDITOR environment variable)
        if editor is None:
            editor = os.environ.get('EDITOR', 'vim')
        
        # Create a temporary file with a recognizable suffix
        with tempfile.NamedTemporaryFile(suffix='.txt', mode='w', delete=False) as tf:
            temp_filename = tf.name
            tf.write(initial_content)
        
        try:
            # Launch the editor and wait for it to close
            subprocess.run([editor, temp_filename], check=True)
            
            # Read the contents of the temporary file
            with open(temp_filename, 'r') as f:
                content = f.read()
        except subprocess.CalledProcessError as e:
            print(f"Editor error: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            # Clean up the temporary file
            os.unlink(temp_filename)
        
        return content
    
    def get_citation_from_arxiv_id(self, arxiv_addr):
        """
        Takes in paper arxiv id, returns string with bibget citation
        """
        
        keys = [arxiv_addr]
        
        bibget = pbg.Bibget(mathscinet=True)
        bib_data = asyncio.run(bibget.citations(keys))
        number_of_entries = len(bib_data.entries)
        bib_data = bib_data.to_string('bibtex')
    
        return bib_data
    
    def obtain_label_from_bibentry(self, bib_entry):
        """
        Obtains label for bibliographic entry from string with .bib entry
        """
        # Process each line to find the label
        for line in bib_entry.splitlines():
            stripped_line = line.strip()
            if stripped_line.startswith('@'):
                # Match the pattern: @<entry_type>{<label>
                match = re.match(r'@([a-z]+)\s*{\s*([^,]+)', stripped_line)
                if match:
                    label = match.group(2)
                    return label

class PaperDownloader():
    def __init__(self, ref_dir: str, arxiv_id: str):
        """
        Class to set up and download the paper from its arxiv id.
        Args:
            ref_dir (str): directory with all the references' data
            arxiv_id (str): id of paper on arxv to download
        """

        self.citerius = CiteriusConfig(ref_dir)
        self.cutils = CiteriusUtils()
        self.check_if_string_is_arxiv_id(arxiv_id)

        if self.download_link == 'nan': # Arxiv paper
            self.citation_str = self.cutils.get_citation_from_arxiv_id(self.arxiv_id)
        else: # Paper with link to download
            editor = "vim"
            self.get_citation_from_tmpfile(editor)

        self.get_arxiv_paper_info()
        
    # Utility functions

    def check_if_string_is_arxiv_id(self, string):
        """
        Checks if the passed string is in arxiv id format.
        Sets up arxiv_id and download_link variables.
        """
        pattern = r'^(\d{4}\.\d{4,5}(v\d+)?|\d{7}(v\d+)?)$'
        if re.match(pattern, string) == None:
            self.arxiv_id = "nan"
            self.download_link = string
        else:
            self.download_link = "nan"
            self.arxiv_id = string

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
        Obtains a bunch of paper information from aixiv id
        """
    
        concat_string = " and " 
        
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
    
        csv_str = f"\"{self.full_title}\",\"{self.full_authors}\",\"{self.arxiv_id}\",\"{self.year}\",\"{self.label}\",\"{self.download_ans}\",\"{self.download_src_ans}\",\"{self.download_link}\""
    
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
            self.append_bibtex()
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
            label = "NaN"
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

    # Download from sources

    def download_paper_general(self):
        """
        General function to identify the method for paper download and download the paper itself
        """
        if self.download_link == 'nan':
            self.download_arxiv_paper()
            print("The paper was downloaded successfully!")
        elif self.arxiv_id == 'nan':
            self.download_paper_from_link()
            print("The paper was downloaded successfully!")
        else:
            print("Unknown situation with arxiv_id and download_link both not being nan.")
            print(f"arxiv_id: {self.arxiv_id}")
            print(f"download_link: {self.download_link}")

    def download_arxiv_paper(self):
        """
        Downloads paper or its source from arxiv
        """
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
            print("Done!")

    def download_paper_from_link(self):
        """
        Downloads the paper from a provided link, not from arxiv
        """
        urlretrieve(self.download_link, self.download_path)

# MAIN CALL

if __name__ == "__main__":
    #ref_dir = sys.argv[1]
    ref_dir = "/home/vasilii/research/references"
    arxiv_id = input("Arxiv paper id / Download link: ")
    paper_download = PaperDownloader(ref_dir, arxiv_id)
    paper_download.download_paper_with_user_input()
