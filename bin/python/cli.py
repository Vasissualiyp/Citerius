import argparse
from paper_downloader import PaperDownloader, BulkDownloader
from config import CiteriusConfig, CiteriusUtils

class CiteriusParser():
    def __init__(self):
        """Create a new instance"""
        self.parse_args()

    def parse_args(self):
        parser = argparse.ArgumentParser(description="Perform certain Citerius ACTION on a specified TARGET")
        
        parser.add_argument('--no-confirm', help='Avoid prompting user for confirmation', action='store_true')
        parser.add_argument('--config', help='Path to Citerius config file. Defaults to $HOME/.config/citerius/config.json', type=str, default=None)
        
        action = parser.add_argument_group('action')
        action.add_argument('--remove', help='Remove target', action='store_true')
        action.add_argument('--download', help='Download target', action='store_true')
        
        target = parser.add_argument_group('target')
        target.add_argument('--label', type=str, help='Label to perform action with', default="")
        target.add_argument('--arxiv', type=str, help='Arxiv number of the paper to perform action with', default="")
        target.add_argument('--link', type=str, help='Link to the paper to perform action with', default="")
        target.add_argument('--pdf', type=str, help='Path to pdf file of the paper to perform action with', default="")
        target.add_argument('--file', type=str, help='Path to file of the collection of papers to perform action with', default="")
        target.add_argument('--fzf', help='Fuzzy find paper label. If no action specified, then returns the label', action='store_true')
        self.args = parser.parse_args()

if __name__ == "__main__":
    parser = CiteriusParser()
