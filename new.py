#!/usr/bin/python3
import curses
from curses import wrapper

# --- Mock Backend Classes (Based on implied structure from Todo.py) ---
# Replace these with your actual lib/Entry.py, lib/EntryList.py, and lib/LoadBackend.py classes.

from lib.LoadBackend import *
from lib.Extras import *
from lib.Entry import *
from lib.EntryList import *
from Todo import *

# --- Ncurses Front-end Classes ---

class BaseView:
    """Base class for all ncurses screen components."""
    def __init__(self, window):
        self.window = window
        self.max_y, self.max_x = self.window.getmaxyx()

    def draw(self):
        """Abstract method to draw the view content."""
        raise NotImplementedError

    def handle_input(self, key):
        """Abstract method to handle a keypress."""
        raise NotImplementedError


class TodoListView(BaseView):
    """A view to display and interact with all todo items."""
    def __init__(self, window, todo_model):
        super().__init__(window)
        self.todo_model = todo_model
        self.flat_items = []
        self._flatten_data()
        self.cursor_y = 0
        self.scroll_y = 0
        self._setup_colors()

    def _setup_colors(self):
        """Initialize color pairs for drawing."""
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)

    def _flatten_data(self):
        """Converts nested lists/entries into a flat list for easy navigation."""
        self.flat_items = []
        for list_obj in self.todo_model.getEntryLists():
            # Add the list header
            self.flat_items.append({'type': 'list', 'data': list_obj})
            # Add the entries
            for entry_obj in list_obj.getEntries():
                self.flat_items.append({'type': 'entry', 'data': entry_obj})

        # Ensure cursor is within bounds after data refresh
        if self.cursor_y >= len(self.flat_items):
            self.cursor_y = max(0, len(self.flat_items) - 1)


    def draw(self):
        """Draws the list of todo items to the window."""
        self.window.clear()
        
        # Display the command bar
        self.window.addstr(0, 0, "[Q]uit [E]dit/Toggle [Up/Down] Move", curses.A_REVERSE)

        # Content drawing starts after the command bar (row 1)
        # Use max_y - 1 to account for the command bar at row 0
        display_height = self.max_y - 1 

        for i, item in enumerate(self.flat_items):
            list_index = i - self.scroll_y
            if 0 < list_index < display_height:
                is_selected = (i == self.cursor_y)
                row_attr = curses.A_NORMAL

                if item['type'] == 'list':
                    text = f"--- {item['data'].getName()} ---"
                    color_pair = curses.color_pair(3)
                else: # type == 'entry'
                    entry = item['data']
                    status = 'X' if entry.isDone() else ' '
                    text = f"  [{status}] {entry.getTitle()}"
                    color_pair = curses.color_pair(1) if entry.isDone() else curses.color_pair(2)
                
                # Apply attributes
                row_attr |= color_pair
                if is_selected:
                    row_attr |= curses.A_REVERSE

                self.window.addstr(list_index, 0, text.ljust(self.max_x), row_attr)
        
        self.window.refresh()


    def handle_input(self, key):
        """Handles keypress events."""
        total_items = len(self.flat_items)
        display_height = self.max_y - 1 # Space available below command bar

        if key in (curses.KEY_UP, ord('k')):
            if self.cursor_y > 0:
                self.cursor_y -= 1
            if self.cursor_y < self.scroll_y:
                self.scroll_y -= 1
        
        elif key in (curses.KEY_DOWN, ord('j')):
            if self.cursor_y < total_items - 1:
                self.cursor_y += 1
            if self.cursor_y >= self.scroll_y + display_height - 1:
                self.scroll_y += 1
        
        elif key in (ord('e'), ord('E')):
            self._toggle_selected_entry()
            self._flatten_data() # Redraw with new status

        return True # Handled the key


    def _toggle_selected_entry(self):
        """Interacts with the backend to toggle an entry's status."""
        if not self.flat_items:
            return

        selected_item = self.flat_items[self.cursor_y]
        
        if selected_item['type'] == 'entry':
            entry = selected_item['data']
            entry.toggleDone()
            # In a real app, you would also save the data here:
            # self.todo_model.save_data() 


class App:
    """The main application class that manages the curses environment and views."""
    def __init__(self):
        self.running = True

    def start(self, todo_model):
        """Initializes curses and runs the main loop."""
        wrapper(self._main_loop, todo_model)

    def _main_loop(self, stdscr, todo_model):
        """The core ncurses application loop."""
        
        # Curses initialization setup
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(True) # Non-blocking input
        stdscr.keypad(True) # Enable special keys (like KEY_UP)
        curses.start_color() # Initialize colors

        # Initialize the main view
        self.current_view = TodoListView(stdscr, todo_model)
        
        # Main event loop
        while self.running:
            # 1. Draw the current view
            self.current_view.draw()
            
            # 2. Get Input
            try:
                key = stdscr.getch()
            except:
                key = -1 # No input received (due to nodelay=True)

            # 3. Handle Input
            if key != -1:
                # Quit keybinds (q, Q)
                if key in (ord('q'), ord('Q')):
                    self.running = False
                # Delegate other input to the current view
                else:
                    self.current_view.handle_input(key)
            
            # Simple pause to reduce CPU usage, can be adjusted
            curses.napms(50) 


if __name__ == "__main__":
    # 1. Instantiate the backend model (Todo.py)
    todo_model = Todo()
    
    # 2. Instantiate and run the ncurses front-end (App from lib.App)
    app = App()
    app.start(todo_model)