import pybibget as pbg
import pybtex as pbt
from config import CiteriusConfig
import os
import sys
import asyncio

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
        
        self.prompt_for_download()
        
        # Change the paper's label in its bibtex citation
        self.citation_str = self.citation_str.replace(arxiv_id, self.label, 1)
        
        # Prepare file-name variables for downloading of the paper/its source
        download_dir = os.path.join(self.citerius.parent_dir, self.label)
        download_name = self.label + '.pdf'
        download_path = os.path.join(download_dir, download_name)
        download_src_dir = os.path.join(download_dir, "src")
        download_src_path = os.path.join(download_src_dir, self.label + ".tar.gz")
        
        try:
            os.mkdir(download_dir)
            self.append_bibtex()
        except:
            overwrite = input(f"There is already a paper with the same label. Overwrite? (y/N)")
            raise NotImplementedError("Overwriting isn't implemented yet")
        
        print(self.citation_str)

    def get_paper_info(self):
        """
        Obtains a bunch of paper information from aixiv id
        """
    
        concat_string = " and " 
        citation_str = get_citation_from_arxiv_id(arxiv_id)
        
        # Extract bibliography data from citation string
        bibdata = pbt.database.parse_string(citation_str, "bibtex").entries[arxiv_id]
        
        full_title = bibdata.fields['title']
        year = bibdata.fields['year']
        full_author_list = bibdata.persons['author']
        full_author_str = ""
        for author in full_author_list:
            full_author_str += concat_string + str(author)
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

    def prompt_for_download(self):
        """
        Prompts for the user before downloading of the paper
        """
        print(f"The paper title is: {self.full_title}\n")
        print(f"The paper author(s) are: {self.full_authors}\n")

        download_ans = input("Would you life to download this paper? (Y/n): ")
        
        if download_ans.lower() == "":
            download_ans = 'y'
        
        if download_ans.lower() not in ['y', 'n']:
            raise ValueError(f"Unknown answer to download question. Exiting...")
        
        download_src_ans = input("Would you life to download the source for this paper? (y/N): ")
        if download_src_ans.lower() == "":
            download_src_ans = 'n'
    
        if download_src_ans.lower() not in ['y', 'n']:
            raise ValueError(f"Unknown answer to download source question. Exiting...")
        
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
    
        csv_str = f"{self.full_title}, {self.full_authors}, {self.arxiv_id}, {self.year}, {self.label}"
    
        csv_file = open(self.citerius.csv_file, "a")
        csv_file.write(csv_str)
        csv_file.close()
    
        bib_file = open(self.citerius.bibtex_file, "a")
        bib_file.write(self.citation_str)
        bib_file.close()
        
#ref_dir = sys.argv[1]
arxiv_id = "2504.18004"
ref_dir = "/home/vasilii/research/references"
paper_download = PaperDownloader(ref_dir, arxiv_id)
