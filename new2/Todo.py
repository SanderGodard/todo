#!/bin/python3
import curses as c
import sys
from os import path, mkdir
import json
import argparse

# Updated imports to reflect renaming
from lib.DataStore import TodoParse
# The App class takes stdscr, so we need curses wrapper
from lib.App import App 


class Todo:
    def __init__(self):
        # Initialize data backend
        self.todo = TodoParse()
        self.todo.load()

        # Start curses environment
        c.wrapper(self.run_app)

    def argparser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-l', '--local', action='store_true', help='Enable local note storage for cwd')
        return parser.parse_args()

    def run_app(self, stdscr):
        """Initializes and runs the curses application."""
        self.args = self.argparser()
        self.app = App(stdscr)
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
