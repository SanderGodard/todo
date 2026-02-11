#!/bin/python3
from os import path, mkdir, environ
import curses as c
from platform import system
from time import sleep, time
import json

from lib.Extras import *
from lib.Entry import *
from lib.EntryList import *
from lib.Listview import *

# Structure
## Display with ncurses??

# App
### Help
### Listview
### Points in list
#### Flair icons
#### Edit


class App:
    def __init__(self):
        # Current status of app
        self.screens = (0, 1) # 0 = choose list, 1 = choose entry
        self.currentScreen = 0
        self.editMode = False

        self.chosenEntryList = False

        # default settings for lists view
        self.scrollx = 1
        self.scrolly = 0
        self.editx = 4
        self.xwinscroll = 0
        self.ywinscroll = 0

        self._setup_colors

        # Input settings
        self.set_shorter_esc_delay_in_os()
        c.initscr()
        c.curs_set(2)
        c.noecho()

        # Functions for printing to screen
        self.listview = Listview(self)

    def _setup_colors(self):
        """Initialize color pairs for drawing."""
        # Settings for displaying
        c.init_pair(FlairSymbols.color[Flairs.prt], c.COLOR_YELLOW, c.COLOR_BLACK) # Preset farger
        c.init_pair(FlairSymbols.color[Flairs.tsk], c.COLOR_BLUE, c.COLOR_BLACK)
        c.init_pair(FlairSymbols.color[Flairs.suc], c.COLOR_GREEN, c.COLOR_BLACK)
        c.init_pair(FlairSymbols.color[Flairs.err], c.COLOR_RED, c.COLOR_BLACK)
        c.init_pair(FlairSymbols.color[Flairs.gen], c.COLOR_BLACK, c.COLOR_WHITE)


    def set_shorter_esc_delay_in_os(self):
        environ.setdefault('ESCDELAY', '25')





    def displayHelp(self):
        helpstr = """Keys             :   Actions

        h                :   Display this help screen
        r                :   Refresh terminal window

        up, down         :   Scroll vertically in the list
        left, right      :   Scroll horizontally in the list

        shift + up|down  :   Move task in list

        +, a             :   Add task to list on cursor
        backspace, d     :   Delete task from list on cursor
            This will ask for confirmation.
              enter, y, backspace   : Yes
              escape, n, c, q       : No

        enter, e         :   Edit task text
            This will allow you to edit selected task
              enter                 : Save
              escape                : Cancel
        space            :   Switch task 'state' on cursor

        esc, q, x        :   Exit program


        Hotkeys for the list menu:
        +, a             :   Add list
        r                :   Rename list
        backspace, delete:   Delete list"""
        helpstr = helpstr.replace("\n\t\t", "\n")
        helpstr = helpstr.replace("    ", " ")

        if self.stdscr.getmaxyx()[0] <= 4:
            helpstr = """Make your terminal
            size larger to read
            all the instructions"""

        self.stdscr.clear()
        for i, line in enumerate(helpstr.splitlines()):
            if i == 0:
                self.wr(line, i, Flairs.inf)
            else:
                self.wr(line, i)

        self.alert("Press any key to exit this menu")

        self.stdscr.move(0, 1)
        self.stdscr.refresh()
        wait = self.stdscr.getch()
        self.resetView()
        return


    def formatTimestamp(self, timestamp):
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime("%d %b %H:%M")


    def run(self, todo):
        match currentScreen: # List view or entry view?
            case 0: # Choose list
                handleList = [(entrylist.getText(), len(entrylist.getEntries()), 
                max(entrylist.getEntries(), key=lambda entry: entry.getTime()).getTime()
                ) for entrylist in todo.getEntryLists()]
                # Må resultere i self.chosenEntryList blir valgt.
            case 1:  # Choose entry in list
                handleList = [(entry.getText(), entry.getFlair(), entry.getTime()) for entry in self.chosenEntryList.getEntries()]
        self.stdscr.clear()
        #Handle printing info to screen

        self.listview.printList(handleList)


        self.stdscr.refresh()
        key = self.cleanInp(self.stdscr.getch())
        match key: # Handle input
            case _ if key in [104, 72]: #h
                self.displayHelp()


    def setstdscr(self, stdscr):
        self.stdscr = stdscr
        self.stdscr.clear()


    def start(self, todo):
        # Curses wrapper, calls main.
        c.wrapper(self.setstdscr())
        
        while True:
            app.run(todo)


    def __repr__(self):
        return f"App({stdscr=})"


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


    def _flatten_data(self):
        """Converts nested lists/entries into a flat list for easy navigation."""
        self.flat_items = []
        for list_obj in self.todo_model.getEntryLists():
            # Add the list header
            self.flat_items.append({'type': 'list', 'data': list_obj})
  
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

def main():
    app = App()
    app.start()


if __name__ == "__main__":
    main()
