import tempfile
import subprocess
import asyncio
import os
import re
import pybibget as pbg

class CiteriusUtils():
    def get_user_input_via_editor(self, initial_content="", editor=None):
        # Determine the editor to use (defaults to vim or $EDITOR environment variable)
        if editor is None:
            editor = os.environ.get('EDITOR', 'vim')
        
        # Create a temporary file with a recognizable suffix
        with tempfile.NamedTemporaryFile(suffix='.txt', mode='w', delete=False) as tf:
            temp_filename = tf.name
            tf.write(initial_content)
        
        try:
            # Launch the editor and wait for it to close
            subprocess.run([editor, temp_filename], check=True)
            
            # Read the contents of the temporary file
            with open(temp_filename, 'r') as f:
                content = f.read()
        except subprocess.CalledProcessError as e:
            print(f"Editor error: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            # Clean up the temporary file
            os.unlink(temp_filename)
        
        return content
    
    def get_citation_from_arxiv_id(self, arxiv_addr):
        """
        Takes in paper arxiv id, returns string with bibget citation
        """
        
        keys = [arxiv_addr]
        
        bibget = pbg.Bibget(mathscinet=True)
        bib_data = asyncio.run(bibget.citations(keys))
        number_of_entries = len(bib_data.entries)
        bib_data = bib_data.to_string('bibtex')
    
        return bib_data
    
    def obtain_label_from_bibentry(self, bib_entry):
        """
        Obtains label for bibliographic entry from string with .bib entry
        """
        # Process each line to find the label
        for line in bib_entry.splitlines():
            stripped_line = line.strip()
            if stripped_line.startswith('@'):
                # Match the pattern: @<entry_type>{<label>
                match = re.match(r'@([A-Za-z]+)\s*{\s*([^,]+)', stripped_line)
                print(match)
                if match:
                    label = match.group(2)
                    return label

    def find_bibtex_entry(self, content, label):
        """
        Obtains bibtex entry from a list of lines, corresponding to bibtex file
        Args:
            content (list of str): bibtex file, separated into list of lines
            (how it's being read by readlines())
            label (str): label of entry of interest
    
        Returns:
            str: multiline string, bibtex entry for label of interest. 
            returns None if bibtex entry for given label wasn't found.
        """
        # Escape special characters in the label to prevent regex issues
        escaped_label = re.escape(label)
        # Construct the regex pattern
        pattern = r'@[a-z]+\{%s\s*,.*?^\s*\}' % escaped_label
        # Compile with flags to handle multiline entries
        regex = re.compile(pattern, flags=re.DOTALL | re.MULTILINE)
        # Search for the pattern in the content
        content_str = ""
        for line in content:
            content_str += line
        match = regex.search(content_str)
        return match.group(0) if match else None
    
    def remove_multiline_block(self, file_path, start_pattern, end_pattern):
        # Create a temporary file in the SAME DIRECTORY as the original file
        file_dir = os.path.dirname(file_path)
        with tempfile.NamedTemporaryFile(
            mode='w', 
            delete=False,
            dir=file_dir  # Critical: Create temp file in same directory/device
        ) as temp_file:
            with open(file_path, 'r') as original_file:
                in_block = False
                for line in original_file:
                    if re.match(start_pattern, line):
                        in_block = True
                    if not in_block:
                        temp_file.write(line)
                    if in_block and re.search(end_pattern, line):
                        in_block = False
    
        # Replace the original file (now guaranteed to be on same device)
        os.replace(temp_file.name, file_path)
    
    def remove_ith_line(self, filename, i):
        temp_filename = f"{filename}.tmp"
        line_count = 0
    
        with open(filename, 'r') as infile, open(temp_filename, 'w') as outfile:
            for line in infile:
                if line_count != i:
                    outfile.write(line)
                line_count += 1
    
        # Replace the original file with the temporary file
        os.replace(temp_filename, filename)

    def check_if_string_is_arxiv_id(self, string):
        """
        Checks if the passed string is in arxiv id format.
        Sets up arxiv_id and download_link variables.
        Returns:
            arxiv_id, download_link: a tuple of strings as they should
            be set in PaperDownloader class (i.e. one of them should be 'nan')
        """
        pattern = r'^(\d{4}\.\d{4,5}(v\d+)?|\d{7}(v\d+)?)$'
        if os.path.isfile(string):
            arxiv_id = "nan"
            download_link = "nan"
            print(f"Identified file as {string}")
        elif re.match(pattern, string) == None:
            arxiv_id = "nan"
            download_link = string
            print(f"Identified download link as {download_link}")
        else:
            download_link = "nan"
            arxiv_id = string
            print(f"Identified arxiv id as {arxiv_id}")
        return arxiv_id, download_link
