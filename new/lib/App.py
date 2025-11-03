#!/bin/python3
import curses as c
import os
from time import sleep

# Relative imports
from .Constants import Keybinds, Flairs, FlairSymbols
from .Entry import Entry
from .EntryList import EntryList
from .Rendering import Rendering


class App:
    """
    Main controller for the ncurses UI. Manages state, handles input,
    and orchestrates rendering via Listview.
    """
    def __init__(self, stdscr):
        # curses window object
        self.window = stdscr
        self.window.keypad(True)
        self.max_y, self.max_x = self.window.getmaxyx()

        # Application state
        self.data_store = None # Set in start()
        self.currentScreen = 0 # 0: List selection, 1: Entry view
        self.chosenEntryList = None # EntryList object when currentScreen is 1
        
        # View state
        self.cursor_y = 0 # Vertical cursor position (index in flat_items)
        self.scroll_y = 0 # Vertical scroll offset (top item index)
        self.scroll_x = 0 # Horizontal scroll offset
        self.flat_items = [] # List of {'type', 'data'} used for rendering
        
        self.set_shorter_esc_delay_in_os()
        c.curs_set(0) # Invisible cursor normally
        c.noecho() # Don't echo input

        self._setup_colors()

        # Rendering helper
        self.listview = Listview(self)

    def set_shorter_esc_delay_in_os(self):
        """Sets the delay for ESC key to prevent input lag."""
        try:
            # Adjust the ncurses timeout for a better ESC key experience
            os.environ['ESCDELAY'] = '25'
        except Exception:
            pass

    def _setup_colors(self):
        """Initialize color pairs for drawing based on FlairSymbols."""
        if c.has_colors():
            c.use_default_colors() # Enable default colors for transparency
            c.start_color()
            
            # --- CHANGE FOR TRANSPARENCY ---
            # Using -1 for the background color tells curses to use the 
            # terminal's current background, achieving a "blank" or 
            # transparent effect.
            BG_COLOR = -1 
            # -------------------------------
            
            # Map symbolic flairs to color definitions
            COLOR_MAP = {
                Flairs.tsk: c.COLOR_WHITE,
                Flairs.suc: c.COLOR_GREEN,
                Flairs.err: c.COLOR_RED,
                Flairs.gen: c.COLOR_CYAN,
                Flairs.inf: c.COLOR_YELLOW, # List headers/Status bar
                Flairs.prt: c.COLOR_MAGENTA,
            }
            
            for flair, color_id in FlairSymbols.COLOR_ID.items():
                fg_color = COLOR_MAP.get(flair, c.COLOR_WHITE)
                # Init pair with the determined foreground color and the transparent background
                c.init_pair(color_id, fg_color, BG_COLOR)
        
    def _flatten_data(self):
        """
        Creates the flat list of items used for navigation and display
        based on the current screen. Also handles sorting of entries.
        """
        self.flat_items = []
        
        if self.currentScreen == 0:
            # List selection view: Show all sorted EntryLists
            for elist in self.data_store.getEntryLists():
                self.flat_items.append({'type': 'list', 'data': elist})
        
        elif self.currentScreen == 1 and self.chosenEntryList:
            # Entry view: Show sorted entries of the selected list
            for entry in self.chosenEntryList.getEntries():
                self.flat_items.append({'type': 'entry', 'data': entry})
        
        # Recalculate view limits
        total_items = len(self.flat_items)
        display_height = self.max_y - 1 

        # Clamp cursor position
        self.cursor_y = min(self.cursor_y, total_items - 1)
        self.cursor_y = max(0, self.cursor_y)
        
        # Clamp scroll position to ensure cursor is always visible
        if self.cursor_y < self.scroll_y:
            self.scroll_y = self.cursor_y
        if self.cursor_y >= self.scroll_y + display_height:
            self.scroll_y = self.cursor_y - display_height + 1
        
        # Final scroll clamp
        self.scroll_y = max(0, self.scroll_y)
        self.scroll_x = max(0, self.scroll_x)


    def _get_selected_item(self):
        """Returns the currently selected item object."""
        if 0 <= self.cursor_y < len(self.flat_items):
            return self.flat_items[self.cursor_y]['data']
        return None

    def _get_selected_item_type(self):
        """Returns the type of the currently selected item ('list' or 'entry')."""
        if 0 <= self.cursor_y < len(self.flat_items):
            return self.flat_items[self.cursor_y]['type']
        return None

    # --- UI Interactions ---

    def _handle_navigation(self, key):
        """Handles cursor movement and scrolling."""
        total_items = len(self.flat_items)
        display_height = self.max_y - 1 # Space available above command bar

        if key in Keybinds.UP:
            if self.cursor_y > 0:
                self.cursor_y -= 1
        
        elif key in Keybinds.DOWN:
            if self.cursor_y < total_items - 1:
                self.cursor_y += 1
        
        # Horizontal scrolling (used when viewing long titles)
        elif key in Keybinds.LEFT:
            self.scroll_x = max(0, self.scroll_x - 4)
        elif key in Keybinds.RIGHT:
            self.scroll_x += 4
        
        self._flatten_data() # Update scroll position after movement

    def _handle_delete(self):
        """Deletes the selected list or entry."""
        item = self._get_selected_item()
        if not item:
            return
            
        item.delete()
        
        # Ensure data integrity after deletion
        if self.currentScreen == 0 and not self.data_store.getEntryLists():
            self.data_store.addEntryList()
            
        elif self.currentScreen == 1 and not self.chosenEntryList.getEntries():
            self.chosenEntryList.addEntry() # A list must have at least one entry

        self._flatten_data()
        
    def _handle_add(self):
        """Adds a new list or entry."""
        if self.currentScreen == 0:
            # Add new EntryList
            self.data_store.addEntryList()
        elif self.currentScreen == 1 and self.chosenEntryList:
            # Add new Entry to the current list
            self.chosenEntryList.addEntry()

        self._flatten_data()
        self.cursor_y = len(self.flat_items) - 1 # Select the new item

    def _handle_rename_or_edit(self):
        """Opens an item for in-place text editing (migrated from todo.py's editMode)."""
        item = self._get_selected_item()
        if not item:
            return
            
        initial_text = item.getTitle()

        # The edit bar is always on the last line
        edit_y = self.max_y - 1 
        
        # Setup for text input
        c.curs_set(1) # Visible cursor
        c.echo() # Echo characters
        self.window.nodelay(False) # Blocking input for editing
        
        new_text = initial_text
        cursor_pos = len(new_text)
        
        while True:
            # Redraw the edit line
            self.window.move(edit_y, 0)
            self.window.clrtoeol()
            
            prompt = "[EDIT]: "
            display_line = prompt + new_text
            
            # Simple horizontal scroll handling for the edit line
            display_start_col = 0
            # If the line is longer than the screen width, calculate scroll offset
            if len(display_line) > self.max_x - 1:
                if cursor_pos + len(prompt) > self.max_x - 1:
                    display_start_col = cursor_pos + len(prompt) - (self.max_x - 1)
                
            # Draw the line
            self.window.addstr(edit_y, 0, display_line[display_start_col:].ljust(self.max_x - 1), c.A_REVERSE)
            
            # Move the actual curses cursor
            cursor_x = len(prompt) + cursor_pos - display_start_col
            self.window.move(edit_y, min(self.max_x - 1, cursor_x))
            self.window.refresh()

            key = self.window.getch()

            if key in Keybinds.ESCAPE:
                # Cancel edit
                break 
            elif key in Keybinds.ENTER:
                # Commit edit
                item.edit(new_text)
                break
            elif key in Keybinds.BACKSPACE:
                if cursor_pos > 0:
                    new_text = new_text[:cursor_pos-1] + new_text[cursor_pos:]
                    cursor_pos -= 1
            elif key in Keybinds.DELETE:
                if cursor_pos < len(new_text):
                    new_text = new_text[:cursor_pos] + new_text[cursor_pos+1:]
            elif key == c.KEY_LEFT:
                cursor_pos = max(0, cursor_pos - 1)
            elif key == c.KEY_RIGHT:
                cursor_pos = min(len(new_text), cursor_pos + 1)
            elif 32 <= key <= 255: # Printable characters
                char = chr(key)
                new_text = new_text[:cursor_pos] + char + new_text[cursor_pos:]
                cursor_pos += 1
            # Ignore other keys (like function keys during echo)
        
        # Restore terminal state after edit
        c.curs_set(0)
        c.noecho()
        self.window.nodelay(True)
        self.window.move(edit_y, 0)
        self.window.clrtoeol() # Clear the edit line
        self._flatten_data() # Refresh data structure and re-render

    def _handle_view_switch(self, key):
        """Handles switching between list selection (0) and entry view (1)."""
        if self.currentScreen == 0:
            # Open list
            item = self._get_selected_item()
            if self._get_selected_item_type() == 'list':
                self.chosenEntryList = item
                self.currentScreen = 1
        
        elif self.currentScreen == 1:
            # Go back to list selection
            self.currentScreen = 0
            self.chosenEntryList = None

        # Reset view state for the new screen
        self.cursor_y = 0
        self.scroll_y = 0
        self.scroll_x = 0
        self._flatten_data()

    def handle_input(self, key):
        """Processes a single keypress event."""
        
        # --- Global Keybinds ---
        if key in Keybinds.QUIT:
            return False # Signal to exit the main loop

        # --- Screen-Agnostic Keybinds ---
        if key in Keybinds.UP or key in Keybinds.DOWN:
            self._handle_navigation(key)
        
        elif key in Keybinds.ADD:
            self._handle_add()
            
        elif key in Keybinds.DELETE_ITEM:
            self._handle_delete()
        
        elif key in Keybinds.RENAME or key in Keybinds.EDIT:
            self._handle_rename_or_edit()
        
        # --- Screen-Specific Keybinds ---
        
        if self.currentScreen == 0:
            # List selection view: ENTER/RIGHT opens list
            if key in Keybinds.ENTER or key in Keybinds.RIGHT:
                self._handle_view_switch(key)
                
        elif self.currentScreen == 1:
            # Entry view: LEFT arrow goes back to list selection
            if key in Keybinds.LEFT:
                self._handle_view_switch(key)
                
            # SPACE flips the flair of the entry
            elif key in Keybinds.FLIP:
                item = self._get_selected_item()
                if self._get_selected_item_type() == 'entry':
                    item.flip()
                    self._flatten_data()
        
        return True # Continue the loop


    def start(self, data_store):
        """
        Main application loop.
        :param data_store: The TodoParse instance containing data.
        """
        self.data_store = data_store
        
        # Initial data load and view setup
        self._flatten_data()
        
        # Set nodelay to non-blocking input
        self.window.nodelay(True)
        
        running = True
        
        while running:
            # 1. Input
            key = self.window.getch()
            
            if key != c.ERR and key != -1:
                running = self.handle_input(key)

            # 2. Rendering
            # Handle terminal resize
            self.max_y, self.max_x = self.window.getmaxyx()
            self._flatten_data() # Recalculate scroll/cursor limits
            self.listview.draw(self.flat_items, self.cursor_y, self.scroll_y, self.scroll_x)
            
            # Simple sleep to prevent high CPU usage
            sleep(0.01)

        # Application loop finished
