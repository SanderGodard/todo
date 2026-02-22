#!/bin/python3
import curses as c
import sys
import os
from os import path, mkdir
import json
import argparse

# Updated imports to reflect renaming
from lib.DataStore import TodoParse
# The App class takes stdscr, so we need curses wrapper
from lib.App import App 


class Todo:
    def __init__(self):
        # Parse arguments first
        self.args = self.argparser()
        
        # Check if user just wants to see keybinds
        if self.args.keybinds:
            self.show_keybinds()
        
        # Determine storage path based on arguments
        self.storage_path = self.get_storage_path()
        
        # Initialize data backend with custom storage path
        self.todo = TodoParse(storage_path=self.storage_path)
        self.todo.load()

        # Ensure ESCDELAY is set early so Escape is responsive
        os.environ.setdefault('ESCDELAY', '25')

        # Start curses environment
        c.wrapper(self.run_app)

    def argparser(self):
        parser = argparse.ArgumentParser(
            description="Todo Application - A terminal-based todo list manager",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Automatically created files:
  ~/.todo/storage.json      Default storage file created in home directory
  ~/.todo/config            Configuration file for colors, divider, status bar format
  .todolist.json            Created in current directory if using -l flag

Examples:
  %(prog)s                      # Use default ~/.todo/storage.json
  %(prog)s -l                   # Use local .todolist.json in current directory
  %(prog)s -t /path/to/file.json # Use custom JSON file
  %(prog)s -k                   # Show keybinds and exit
            """
        )
        parser.add_argument(
            '-l', '--local',
            action='store_true',
            help='Use a local .todolist.json file in the current working directory (creates if not exists)'
        )
        parser.add_argument(
            '-t', '--todolist',
            type=str,
            metavar='FILE',
            help='Specify a custom path to the todo list JSON file'
        )
        parser.add_argument(
            '-k', '--keybinds',
            action='store_true',
            help='Display all keybinds for the application'
        )
        return parser.parse_args()
    
    def show_keybinds(self):
        """Display all available keybinds."""
        keybinds_text = """
╔════════════════════════════════════════════════════════════════════════════╗
║                          TODO APPLICATION KEYBINDS                         ║
╚════════════════════════════════════════════════════════════════════════════╝

COMMON KEYBINDS (All Screens)
─────────────────────────────────────────────────────────────────────────────
  H, Left               Navigate left (horizontal scrolling)
  L, Right              Navigate right (horizontal scrolling)
  J, S, Down            Move cursor down (wraps around)
  K, W, Up              Move cursor up (wraps around)
  Home                  Jump to first entry
  End                   Jump to last entry

  Q, X, Esc, Ctrl+X     Go back (exit entry view or quit app)
  
  +, A                  Add a new entry at cursor
  D, Del, Backspace     Delete entry at cursor
  
  R, E, I, Enter        Edit entry (See EDITING SCREEN for details)

LIST SELECTION SCREEN (Screen 0)
─────────────────────────────────────────────────────────────────────────────
  -

ENTRY VIEW SCREEN (Screen 1)
─────────────────────────────────────────────────────────────────────────────  
  Space                 Toggle entry flair (cycle through states)
  
  Shift + Up            Move entry up in list
  Shift + Down          Move entry down in list
  
  Tab                   Indent entry (add 4 spaces at start)
  Shift+Tab             Unindent entry (remove up to 4 spaces from start)
  
EDITING SCREEN (When editing entry/list text)
─────────────────────────────────────────────────────────────────────────────
  Left, Right           Move cursor within text
  Shift+Left            Move cursor to previous word
  Shift+Right           Move cursor to next word
  Backspace             Delete character before cursor
  Delete                Delete character at cursor
  Ctrl/Shift+Delete     Delete entire word at/after cursor
  Ctrl/Shift+Backspace  Delete entire word at/after cursor
  
  Tab                   Indent entry (add 4 spaces at start)
  Shift+Tab             Unindent entry (remove up to 4 spaces from start)
  
  Enter, Ctrl+O         Save changes
  Esc, Ctrl+X           Cancel editing (revert changes)

═════════════════════════════════════════════════════════════════════════════
"""
        print(keybinds_text)
        sys.exit(0)
    
    def get_storage_path(self):
        """Determine the storage path based on command-line arguments."""
        if self.args.todolist:
            return self.args.todolist
        elif self.args.local:
            return path.join(os.getcwd(), '.todolist.json')
        else:
            # Default: let TodoParse use ~/.todo/storage.json
            return None

    def run_app(self, stdscr):
        """Initializes and runs the curses application."""
        self.app = App(stdscr, storage_path=self.storage_path)
        # Pass the loaded data store to the application controller
        self.app.start(self.todo)

    def __str__(self):
        return f"{self.__class__.__name__}(Storage: {self.todo.storage}, Lists: {len(self.todo.entryLists)})"

    def __repr__(self):
        return f"<{self.__class__.__name__}>"


def main():
    try:
        # The entire application runs within the Todo object's __init__ and run_app
        Todo()
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        # Re-raise for full traceback if needed, but printing is safer for ncurses environment
        # raise

if __name__ == "__main__":
    main()
