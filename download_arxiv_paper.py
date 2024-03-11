import arxiv
import sys

paper_id = sys.argv[1]
print(f"{paper_id}")
download_path = sys.argv[2]
print(f"{download_path}")
paper_name = sys.argv[3]
print(f"{paper_name}")

paper = next(arxiv.Client().results(arxiv.Search(id_list=[paper_id])))

paper.download_pdf(dirpath=download_path, filename=paper_name)
