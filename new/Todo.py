#!/bin/python3
import curses as c
import sys # Added for graceful exit handling

# Imports for the core application logic (assuming a 'lib' directory)
from lib.DataStore import TodoParse
from lib.App import App

class Todo:
    """
    Main controller class for the Todo application.
    It orchestrates the data backend (TodoParse) and the user interface (App).
    """
    def __init__(self, stdscr):
        # Initialize data backend
        self.data_store = TodoParse()
        self.data_store.validateStorage()
        self.data_store.load()

        # Initialize the application UI
        self.app = App(stdscr)

    def run(self):
        """Starts the ncurses application loop."""
        print("Starting application...") # Debug
        try:
            # Pass the data store to the App instance for manipulation
            self.app.start(self.data_store)
        except Exception as e:
            # Print error to terminal before crashing
            print(f"An unexpected error occurred during the app loop: {e}", file=sys.stderr)
        finally:
            # Always save the data when the app exits
            self.data_store.save()
            print("Data saved. Application exiting.")

    def __str__(self):
        return f"{self.__class__.__name__}(Data Store path={self.data_store.storage}, Lists={len(self.data_store.entryLists)})"

def main(stdscr):
    """
    Entry point for the ncurses wrapper.
    """
    # Attempt to set shorter ESC delay for better responsiveness
    try:
        stdscr.timeout(50) 
    except:
        pass

    try:
        # Pass the stdscr (main window) to the Todo controller
        todo_app = Todo(stdscr)
        todo_app.run()
    except Exception as e:
        # Simple error display for ncurses mode before final exit
        stdscr.clear()
        stdscr.addstr(0, 0, f"FATAL ERROR: {e}")
        stdscr.refresh()
        stdscr.getch() 

if __name__ == "__main__":
    # The curses wrapper initializes the screen and restores the terminal state on exit
    c.wrapper(main)
