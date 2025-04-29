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


arxiv_id = "2504.18004"
concat_string = " and " 
citation_str = get_citation_from_arxiv_id(arxiv_id)

bibdata = pbt.database.parse_string(citation_str, "bibtex").entries[arxiv_id]

full_title = bibdata.fields['title']
year = bibdata.fields['year']
full_author_list = bibdata.persons['author']
full_author_str = ""
for author in full_author_list:
    full_author_str += concat_string + str(author)
first_author = full_author_list[0]
full_author_str = full_author_str[len(concat_string):]
print(full_author_str)
