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

def get_paper_info(arxiv_id: str):
    """
    Obtains a bunch of paper information from aixiv id

    Args:
        arxiv_id (str): id of paper on arxv

    Returns:
        citation_str: string with citation in bibtex format
        full_title: string with full paper title
        full_author_str: string with full paper author
        year: string with the year of paper's release
        default_label: string with the default label for the paper
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

    return citation_str, full_title, full_author_str, year, default_label

def prompt_for_download(default_label):
    """
    Prompts for the user before downloading of the paper
    Args:
        default_label (str): default label for the paper if no argument was passed

    Returns:
        string for download paper prompt
        string for download source prompt
        string for label of the paper
    """
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
        label = default_label

    return download_ans.lower(), download_src_ans.lower(), label

def append_bibtex(citerius: CiteriusConfig):
    """
    Appends bibtex entry to the bibliography file

    Args:
        citerius (CiteriusConfig)
    """
    pass


#ref_dir = sys.argv[1]
arxiv_id = "2504.18004"
ref_dir = "/home/vasilii/research/references"
citerius = CiteriusConfig(ref_dir)

citation_str, full_title, full_authors, year, default_label = get_paper_info(arxiv_id)

print(f"The paper title is: {full_title}\n")
print(f"The paper author(s) are: {full_authors}\n")
download_ans, download_src_ans, label = prompt_for_download(default_label)

# Change the paper's label in its bibtex citation
citation_str = citation_str.replace(arxiv_id, label, 1)

# Prepare file-name variables for downloading of the paper/its source
download_dir = os.path.join(citerius.parent_dir, label)
download_name = label + '.pdf'
download_path = os.path.join(download_dir, download_name)
download_src_dir = os.path.join(download_dir, "src")
download_src_path = os.path.join(download_src_dir, label + ".tar.gz")

try:
    os.mkdir(download_dir)
    append_bibtex(citerius)
except:
    print(f"There is already a paper with the same label. Overwrite?")
    raise NotImplementedError("Overwriting isn't implemented yet")

print(citation_str)
