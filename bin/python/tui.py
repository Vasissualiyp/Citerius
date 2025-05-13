import sys
from functools import partial
from typing import List, Tuple
from readchar import readkey
from rich.console import Console
from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.ansi import AnsiDecoder
from rich.color import Color
from time import sleep

class CiteriusTUI:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.running = True
        
        # Menu state
        self.current_menu = []
        self.selected_idx = 0
        self.menu_stack = []
        self.status_message = ""
        self._init_menus()
        
        # Keybindings
        self.BINDINGS = {
            'j': partial(self._move_selection, 1),
            'up': partial(self._move_selection, 1),
            'k': partial(self._move_selection, -1),
            'down': partial(self._move_selection, -1),
            '\r': self._execute_selection,  # Enter key
            '\n': self._execute_selection,  # Alternate Enter key
            'q': self._exit,
            'h': partial(self._set_status, "Help: j/k - Navigate | Enter - Select | q - Quit"),
        }
        
        # Styles
        self.styles = {
            'header': Style(color="bright_cyan", bold=True),
            'selected': Style(color="bright_white", bgcolor="rgb(40,40,40)", bold=True),
            'unselected': Style(color="bright_black"),
            'status': Style(color="bright_green", bgcolor="black"),
            'panel': Style(bgcolor="rgb(20,20,20)"),
        }

    def _init_menus(self):
        self.menus = {
            'main': [
                ("📚 Browse/Manage Papers", self.browse_papers_menu),
                ("➕ Add Papers", self.add_paper_menu),
                ("🌐 Sync Manager", self.sync_menu),
                ("🚪 Exit", self._exit),
            ],
            'browse': [
                ("🔍 Read Paper (Fuzzy Find)", self.fuzzy_find_paper),
                ("🏷️ Get Paper Label", self.get_paper_label),
                ("🗑️ Remove Paper", self.remove_paper),
                ("↩ Return", partial(self._set_menu, 'main')),
            ],
            'add': [
                ("📄 Add arXiv Paper", self.add_arxiv_paper),
                ("🌍 Add Web Link", self.add_web_paper),
                ("📂 Add PDF Paper", self.add_pdf_paper),
                ("↩ Return", partial(self._set_menu, 'main')),
            ],
            'sync': [
                ("🔄 Sync with Remote Repository", self.sync_repository),
                ("↩ Return", partial(self._set_menu, 'main')),
            ],
        }
        self._set_menu('main')

    def _set_menu(self, menu_name: str):
        self.current_menu = self.menus[menu_name]
        self.selected_idx = 0
        self._clear_status()

    def _move_selection(self, direction: int):
        new_idx = self.selected_idx + direction
        if 0 <= new_idx < len(self.current_menu):
            self.selected_idx = new_idx

    def _execute_selection(self):
        if self.current_menu:
            label, action = self.current_menu[self.selected_idx]
            action()

    def _exit(self):
        self.running = False

    def _create_header(self) -> Text:
        header_text = Text(" CITERIUS REFERENCE MANAGER ", style="bold rgb(128,255,255) on rgb(20,20,20)")
        header_text.stylize("gradient(90, rgb(128,255,255), rgb(0,128,255))", 0, 27)
        return Panel(header_text, style="rgb(60,60,60)")

    def _create_menu_panel(self) -> Panel:
        menu_text = Text()
        for i, (label, _) in enumerate(self.current_menu):
            if i == self.selected_idx:
                menu_text.append(f"⮞ {label}", style=self.styles['selected'])
            else:
                menu_text.append(f"  {label}", style=self.styles['unselected'])
            menu_text.append("\n")
        
        return Panel(
            menu_text,
            title="[bold]Menu[/]",
            style=self.styles['panel'],
            padding=(1, 4)
        )

    def _create_status_bar(self) -> Panel:
        status_text = Text(self.status_message, style=self.styles['status'])
        return Panel(
            status_text,
            style="dim",
            height=3,
            padding=(0, 1)
        )

    def _build_interface(self) -> Layout:
        self.layout.split(
            Layout(self._create_header(), name="header", size=5),
            Layout(self._create_menu_panel(), name="main"),
            Layout(self._create_status_bar(), name="status", size=3)
        )
        return self.layout

    def _set_status(self, message: str):
        self.status_message = message
        self._create_status_bar

    def _clear_status(self):
        self.status_message = ""

    def main_loop(self):
        with Live(self.layout, refresh_per_second=24, screen=True) as live:
            while self.running:
                self.layout.update(self._build_interface())
                key = readkey()
                
                if key in self.BINDINGS:
                    self.BINDINGS[key]()
                elif key == '\x1b':  # Escape character
                    key += readkey()  # Read [
                    key += readkey()  # Read actual arrow key character
                    
                    if key == '\x1b[A':  # Up arrow
                        self._move_selection(-1)
                    elif key == '\x1b[B':  # Down arrow
                        self._move_selection(1)
                
                # Auto-clear status messages after delay
                if self.status_message and "..." in self.status_message:
                    sleep(1)
                    self._clear_status()

    # Menu handlers
    def browse_papers_menu(self): self._set_menu('browse')
    def add_paper_menu(self): self._set_menu('add')
    def sync_menu(self): self._set_menu('sync')

    # Action methods
    def fuzzy_find_paper(self): 
        self._set_status("🔍 Launching fuzzy find interface...")
        sleep(1)

    def get_paper_label(self):
        self._set_status("🏷️ Fetching paper labels...")
        sleep(1)

    def remove_paper(self):
        self._set_status("🗑️ Removing selected paper...")
        sleep(1)

    def add_arxiv_paper(self):
        self._set_status("📄 Adding arXiv paper...")
        sleep(1)

    def add_web_paper(self):
        self._set_status("🌍 Adding web link...")
        sleep(1)

    def add_pdf_paper(self):
        self._set_status("📂 Adding PDF document...")
        sleep(1)

    def sync_repository(self):
        self._set_status("🔄 Syncing with remote repository...")
        sleep(1)

if __name__ == "__main__":
    try:
        app = CiteriusTUI()
        app.main_loop()
    except KeyboardInterrupt:
        sys.exit(0)
