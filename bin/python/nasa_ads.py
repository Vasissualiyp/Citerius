#import ads
#token_file_path = 'ads_token.txt'
#
#with open(token_file_path, 'r') as file:
#    token = file.read()
#token, _ = token.split('\n')
#ads.config.token = token
import ads.sandbox as ads

papers = ads.SearchQuery(q="supernova", sort="citation_count")
for paper in papers:
    print(paper.bibtex)
