import argparse
from paper_downloader import PaperDownloader, BulkDownloader
from config import CiteriusConfig, CiteriusUtils

class CiteriusParser():
    def __init__(self):
        """Create a new instance"""
        self.parse_args()
        self.avoid_multiple_definitions()

        # Do whatever action user asked for
        if self.args.download: self.download()
        elif self.args.remove: self.remove()
        elif self.args.fzf: 
            self.get_fzf_label()
            print(self.args.label)
        else:
            print(f"No action or --fzf was specified")
        print(self.args)

    def parse_args(self):
        """Parse all the CLI arguments"""
        parser = argparse.ArgumentParser(description="Perform certain Citerius ACTION on a specified TARGET")
        
        parser.add_argument('--no-confirm', help='Avoid prompting user for confirmation', action='store_true')
        parser.add_argument('--config', help='Path to Citerius config file. Defaults to $HOME/.config/citerius/config.json', type=str, default=None)
        
        action = parser.add_argument_group('action')
        action.add_argument('--remove', help='Remove target. Only works with fzf or label targets', action='store_true')
        action.add_argument('--download', help='Download/add target', action='store_true')
        
        target = parser.add_argument_group('target')
        target.add_argument('--auto', type=str, help='The program automatically picks the type of targets below (except fzf)', default=False)
        target.add_argument('--label', type=str, help='Label to perform action with', default=False)
        target.add_argument('--arxiv', type=str, help='Arxiv number of the paper to perform action with', default=False)
        target.add_argument('--link', type=str, help='Link to the paper to perform action with', default=False)
        target.add_argument('--pdf', type=str, help='Path to pdf file of the paper to perform action with', default=False)
        target.add_argument('--file', type=str, help='Path to file of the collection of papers to perform action with', default=False)
        target.add_argument('--fzf', help='Fuzzy find paper label. If no action specified, then returns the label', action='store_true')
        self.args = parser.parse_args()

    def avoid_multiple_definitions(self):
        """Throw errors if several targets/actions are declared"""
        args = self.args

        targets = [ args.auto, args.label, args.arxiv, args.link, args.pdf, args.file ]
        targets_err = "Several targets detected. Please, use only one target call"
        self.find_double_definitions_in_list(targets, targets_err)

        actions = [ args.remove, args.download ]
        actions_err = "Several actions detected. Please, use only one action call"
        self.find_double_definitions_in_list(actions, actions_err)

        if args.fzf and any(targets) != False:
            raise ValueError(f"Cannot call fzf with target specified")

    def find_double_definitions_in_list(self, ls: list, error_string:str):
        """A function to raise error if there are several non-empty values in the list

        Args:
            ls: list of values
            error_string: error to throw when condition is triggered
        """
        for target in ls:
            if target:
                count = 0
                for secondary_target in ls:
                    if secondary_target: count+=1
                if count > 1:
                    raise ValueError(error_string)

    def download(self):
        pass

    def remove(self):
        pass

    def get_fzf_label(self):
        pass

if __name__ == "__main__":
    parser = CiteriusParser()
