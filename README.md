# Citerius

> A terminal-centric reference manager for researchers who live in the command line

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
<!-- Add more badges as needed: GitHub stars, version, etc. -->

## Overview

Citerius is a lightweight yet powerful reference manager designed for researchers who prefer working in the terminal. It simplifies the process of downloading, organizing, searching, and citing academic papers—all from the comfort of your command line.

No more context switching between different GUI applications—Citerius integrates seamlessly with your terminal-based workflow, including tools like Zathura, XournalPP, and LaTeX.

## Features

- **Paper Acquisition**
  - Download papers directly from arXiv links
  - Import papers from generic URLs
  - Automatically fetch source code for arXiv papers

- **Search & Organization**
  - Fuzzy-find capabilities for quickly locating papers in your database
  - Customizable metadata tagging and organization

- **Viewing & Annotation**
  - Open PDFs directly with Zathura or XournalPP
  - Maintain your terminal workflow without disruption

- **Citation Management**
  - Hassle-free LaTeX citations
  - BibTeX support
  - Citation history tracking via Git

- **Synchronization**
  - Cross-device synchronization through Git
  - Conflict-free collaboration

## Installation

```bash
# Clone the repository
git clone https://github.com/Vasissualiyp/Citerius.git

# Navigate to the project directory
cd citerius

# Install dependencies
pip install -r requirements.txt  # If Python-based

# Make the main script executable
chmod +x citerius.sh

# Optional: Add to PATH
ln -s "$(pwd)/citerius.sh" ~/.local/bin/citerius
```

## Dependencies

- [Zathura](https://pwmt.org/projects/zathura/) or [XournalPP](https://github.com/xournalpp/xournalpp) for PDF viewing
- Git for version control and synchronization
- [fzf](https://github.com/junegunn/fzf) for fuzzy finding

## Usage

### Basic Commands

```bash
# Download a paper from arXiv
citerius download arxiv 2104.13478

# Download a paper from a URL
citerius download url https://example.com/paper.pdf

# Search through your papers
citerius search "neural networks"

# Open a paper with Zathura
citerius open "Smith et al 2023"

# Open a paper with XournalPP for annotation
citerius annotate "Smith et al 2023"

# Generate a citation for LaTeX
citerius cite "Smith et al 2023"

# Remove a paper from the database
citerius remove "Smith et al 2023"

# Synchronize your database with Git
citerius sync
```

### Configuration

TBD

## Advanced Features

### Working with arXiv Source Code

TBD

### Git Integration

Citerius tracks your citation database with Git, allowing for:

- Version history of your research database
- Easy synchronization across multiple devices
- Collaboration with colleagues (with proper merge handling)

TBC

## Upcoming Features

- **Neovim Plugin**: Seamless integration with Neovim for citing and viewing papers without leaving your editor
- **Content Search**: Search through equations and figures within papers
- **Figure & Equation Extraction**: Easily extract and paste equations and figures into your documents
- **Interactive Previews**: Preview papers/figures/equations in Telescope via the kitty graphics protocol

## Troubleshooting

TBD

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

<!-- Add acknowledgements as needed -->
- Inspired by [papis](https://github.com/papis/papis)
- Thanks to the arXiv API for making research papers accessible
