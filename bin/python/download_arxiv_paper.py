import arxiv
import sys

def download_paper(paper_id, 
                   download_path, 
                   paper_name, 
                   source_download):
    """
    Downloads paper or its source from arxiv

    Args:
        paper_id (str): paper address on arxiv
        download_path (str): path into which to download the paper
        paper_name (str): label of the paper after download
        source_download(str): whether to download src of the paper or just the pdf
    """
    paper = next(arxiv.Client().results(arxiv.Search(id_list=[paper_id])))
    
    if (source_download == "source"):
        paper.download_source(dirpath=download_path, filename=paper_name)
    else:
        paper.download_pdf(dirpath=download_path, filename=paper_name)

if __name__ == "__main__":
    
    paper_id = sys.argv[1]
    download_path = sys.argv[2]
    paper_name = sys.argv[3]
    source_download = sys.argv[4]
    
    download_paper(paper_id, download_path, paper_name, source_download)
