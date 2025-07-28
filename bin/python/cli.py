import argparse, os
from paper_downloader import PaperDownloader, BulkDownloader
from config import CiteriusConfig, CiteriusUtils

class CiteriusParser():
    def __init__(self):
        """Create a new instance"""
        self.parse_args()
        self.avoid_multiple_definitions()

        # Get fuzzy-finding out of the way
        if self.args.fzf:
            self.get_fzf_label()

        # Do whatever action user asked for
        if self.args.download: self.download()
        elif self.args.remove: self.remove()
        elif self.args.fzf: 
            print(self.args.label)
        else:
            print(f"No action or --fzf was specified")

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
        target.add_argument('--all', help='All papers in the dataframe', default=False, action='store_true')
        self.args = parser.parse_args()

    def avoid_multiple_definitions(self):
        """Throw errors if several targets/actions are declared"""
        args = self.args

        targets = [ args.auto, args.label, args.arxiv, args.link, 
                   args.pdf, args.file, args.all ]
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
        bulk_download_flag = False

        if self.args.label:
            raise NotImplementedError
        elif self.args.auto:
            arxiv_id = self.args.auto
        elif self.args.arxiv:
            arxiv_id = self.args.arxiv
        elif self.args.link:
            arxiv_id = self.args.link
        elif self.args.pdf:
            raise NotImplementedError
        elif self.args.file:
            arxiv_id = self.args.file
            bulk_download_flag = True
        elif self.args.all:
            pass # Work with dataframe download below
        else:
            arxiv_id = input("Arxiv paper id / Download link / File path: ")
            if os.path.isfile(arxiv_id):
                bulk_download_flag = True

        if bulk_download_flag:
            bulk_download = BulkDownloader(self.args.config)
            bulk_download.download_from_file(arxiv_id)
            bulk_download.citerius.repo.close()
        elif self.args.all:
            bulk_download = BulkDownloader(self.args.config)
            bulk_download.download_from_citerius()
            bulk_download.citerius.repo.close()
        else:
            paper_download = PaperDownloader(self.args.config, arxiv_id)
            if self.args.no_confirm: paper_download.download_paper_without_user_input()
            else: paper_download.download_paper_with_user_input()
            paper_download.citerius.repo.close()

    def remove(self):
        citerius = CiteriusConfig(self.args.config)

        # Get label of the paper
        if self.args.label:
            label = self.args.label
            id_string = f"label {label}"
        elif self.args.auto:
            raise NotImplementedError
        elif self.args.arxiv:
            raise NotImplementedError
        elif self.args.link:
            raise NotImplementedError
        elif self.args.pdf:
            raise NotImplementedError
        elif self.args.file:
            raise NotImplementedError
        elif self.args.all:
            raise NotImplementedError
        else:
            raise ValueError(f"Target for removal not specified")

        # Prompt the user if the paper really needs to be deleted
        if self.args.no_confirm:
            answer = 'y'
        else:
            answer = input(f"You are about to remove paper with {id_string}. Are you sure? (y/N): ")

        # Delete the paper
        if answer.lower() == 'y':
            citerius.remove_paper(label)
            print(f"The paper with id '{id_string}' was successfully removed.")
            citerius.repo.close()
        else:
            print(f"You answered '{answer}'. The paper will not be removed.")


    def get_fzf_label(self):
        citerius = CiteriusConfig(self.args.config)
        self.args.label = citerius.fuzzy_find_label()

if __name__ == "__main__":
    parser = CiteriusParser()
