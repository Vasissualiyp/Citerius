import arxiv
import sys

paper_id = sys.argv[1]
print(f"{paper_id}")
download_path = sys.argv[2]
print(f"{download_path}")
paper_name = sys.argv[3]
print(f"{paper_name}")
source_download = sys.argv[4]
print(f"{source_download}")

paper = next(arxiv.Client().results(arxiv.Search(id_list=[paper_id])))

if (source_download == "source"):
    paper.download_source(dirpath=download_path, filename=paper_name)
else:
    paper.download_pdf(dirpath=download_path, filename=paper_name)
