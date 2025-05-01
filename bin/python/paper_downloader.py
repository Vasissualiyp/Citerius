import pybibget as pbg
import pybtex as pbt
from config import CiteriusConfig
from pathlib import Path
import os
import sys
import asyncio
import arxiv

def get_citation_from_arxiv_id(arxiv_addr):
    """
    Takes in paper arxiv id, returns string with bibget citation
    """
    
    keys = [arxiv_addr]
    
    bibget = pbg.Bibget(mathscinet=True)
    bib_data = asyncio.run(bibget.citations(keys))
    number_of_entries = len(bib_data.entries)
    bib_data = bib_data.to_string('bibtex')

    return bib_data

class PaperDownloader():
    def __init__(self, ref_dir: str, arxiv_id: str):
        """
        Class to set up and download the paper from its arxiv id.
        Args:
            ref_dir (str): directory with all the references' data
            arxiv_id (str): id of paper on arxv to download
        """

        self.citerius = CiteriusConfig(ref_dir)
        self.arxiv_id = arxiv_id
        self.get_paper_info()
        
    def download_paper_with_user_input(self):
        """
        Downloads the paper with required user input
        """
        self.prompt_for_download()
        
        # Change the paper's label in its bibtex citation
        self.citation_str = self.citation_str.replace(arxiv_id, self.label, 1)
        
        self.setup_download_paths()

        try:
            os.mkdir(self.download_dir)
            self.append_bibtex()
        except:
            print(f"There is already a paper with the label {self.label}")

        self.overwrite_prompt()
        self.download_paper()
        print("The paper was downloaded successfully!")
    
    def setup_download_paths(self):
        """
        Sets up relevant paths for downloading of the paper or its source
        """
        self.download_dir = os.path.join(self.citerius.parent_dir, self.label)
        self.download_name = self.label + '.pdf'
        self.download_path = os.path.join(self.download_dir, self.download_name)
        self.download_src_dir = os.path.join(self.download_dir, "src")
        self.download_src_path = os.path.join(self.download_src_dir, self.label + ".tar.gz")

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

    def get_paper_info(self):
        """
        Obtains a bunch of paper information from aixiv id
        """
    
        concat_string = " and " 
        citation_str = get_citation_from_arxiv_id(self.arxiv_id)
        
        # Extract bibliography data from citation string
        bibdata = pbt.database.parse_string(citation_str, "bibtex").entries[self.arxiv_id]
        
        full_title = bibdata.fields['title']
        year = bibdata.fields['year']
        full_author_list = bibdata.persons['author']
        full_author_str = ""
        for author in full_author_list:
            author_str = str(author)
            lastname =  str(author_str.split()[0])
            firstname = str(author_str.split()[1])
            lastname_alpha = ''.join(char for char in lastname if char.isalpha())
            firstname_alpha = ''.join(char for char in firstname if char.isalpha())
            full_author_str += concat_string + lastname_alpha + " " + firstname_alpha[0]
        full_author_str = full_author_str[len(concat_string):]
    
        # Create default label
        first_author = full_author_list[0]
        first_author_lastname = str(first_author).split()[1].strip()
        first_word_title = str(full_title).split()[0].strip()
        first_word_title_alpha = ''.join(char for char in first_word_title if char.isalpha())
        default_label = first_author_lastname + first_word_title_alpha + year
    
        # Save info as class variables
        self.citation_str = citation_str
        self.full_title = full_title
        self.full_authors = full_author_str
        self.year = year
        self.default_label = default_label

    def download_paper(self):
        """
        Downloads paper or its source from arxiv
        """
        paper = next(arxiv.Client().results(arxiv.Search(id_list=[self.arxiv_id])))
        
        if (self.download_ans == 'y'):
            paper.download_source(dirpath=self.download_dir, 
                                  filename=self.download_name)
        if (self.download_src_ans == 'y'):
            paper.download_pdf(dirpath=self.download_src_dir, 
                               filename=self.download_name)

    def prompt_for_download(self):
        """
        Prompts for the user before downloading of the paper
        """
        print(f"The paper title is: {self.full_title}\n")
        print(f"The paper author(s) are: {self.full_authors}\n")

        download_ans = self.input_with_default("Would you life to download this paper? (Y/n): ", "y")
        
        download_src_ans = self.input_with_default("Would you life to download the source for this paper? (y/N): ", "n")
        
        if (download_ans.lower() == 'n' and download_src_ans.lower() == 'n'):
            print("No download will happen. Exiting...")
        
        label = input("What would be the paper's label? (leave empty for default): ")
        if label == "":
            label = self.default_label
    
        self.download_ans = download_ans.lower()
        self.download_src_ans = download_src_ans.lower()
        self.label = label

    def append_bibtex(self):
        """
        Appends bibtex entry to the bibliography file,
        as well as this paper's string to csv file
        """
    
        csv_str = f"\"{self.full_title}\",\"{self.full_authors}\",\"{self.arxiv_id}\",\"{self.year}\",\"{self.label}\""
    
        csv_file = open(self.citerius.csv_file, "a")
        csv_file.write(csv_str)
        csv_file.close()
    
        bib_file = open(self.citerius.bibtex_file, "a")
        bib_file.write("\n")
        bib_file.write(self.citation_str)
        bib_file.close()
        
if __name__ == "__main__":
    #ref_dir = sys.argv[1]
    #arxiv_id = "2504.18006"
    ref_dir = "/home/vasilii/research/references"
    arxiv_id = input("Arxiv paper id: ")
    paper_download = PaperDownloader(ref_dir, arxiv_id)
    paper_download.download_paper_with_user_input()
