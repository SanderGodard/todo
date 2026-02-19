# Todo 
Now in **v2.0\***
\* After being vibecoded beyond recognition

Small todo list program written in python 3 using the curses library

## Install
```sh
curl https://raw.githubusercontent.com/SanderGodard/todo/refs/heads/main/install.sh | bash
```

## Future work
### Rofi integration possible?
```bash
rofi -no-laz-grab -sep "|" -dmenu -i -p 'Todo ' -mesg "$(./rofi_output.py -mesg)" <<< $(./rofi_output.py)

rofi -no-laz-grab -sep "|" -dmenu -i -p 'Todo ' -mesg "$(./rofi_output.py -mesg)" <<< $(./rofi_output.py -list general)
```

## Overview
Written in python, uses json to store and work with the data

## Architecture

### Main Entry Point
- **Todo.py** - Main entry point that initializes the application, loads data, and starts the curses interface

### Library Structure (lib/)
- **App.py** - Main controller handling user input, navigation, and application state
- **Constants.py** - All constants including Keybinds, Flairs, FlairSymbols, and ColorPairs
- **DataStore.py** - Handles data persistence (the TodoParse class)
- **Entry.py** - Individual task/entry model class
- **EntryList.py** - Collection of entries (represents a single todo list)
- **Rendering.py** - All visual output and screen rendering logic

## Running the Application
```bash
python3 Todo.py                    # Uses default ~/.todo/storage.json
python3 Todo.py -l                 # Uses local .todolist.json in current directory
python3 Todo.py -t /path/to/list   # Uses custom path for todo file
python3 Todo.py -k                 # Show all keybinds
```

For more info on keybinds, see own section below

### Automatically Created Files

On first run, the application automatically creates:

- **~/.todo/storage.json** - Default storage file for your todo lists (created in home directory)
- **~/.todo/config** - Configuration file for customizing colors, divider character, and status bar format
- **.todolist.json** - Local storage file created in current directory when using the `-l` flag

All data is stored in JSON format for easy editing or importing into other tools.

## Keybinds
```

╔════════════════════════════════════════════════════════════════════════════╗
║                          TODO APPLICATION KEYBINDS                         ║
╚════════════════════════════════════════════════════════════════════════════╝

COMMON KEYBINDS (All Screens)
─────────────────────────────────────────────────────────────────────────────
  h, Left           Navigate left (horizontal scrolling)
  l, Right          Navigate right (horizontal scrolling)
  q, Q, x, X, Ctrl+X    Quit the application / Go back to list view

LIST SELECTION SCREEN (Screen 0)
─────────────────────────────────────────────────────────────────────────────
  j, s, Down        Move cursor down (wraps around)
  k, w, Up          Move cursor up (wraps around)
  Home              Jump to first list
  End               Jump to last list

  + or a, A         Add a new list
  d or D            Delete current list (will ask for confirmation)
  Backspace, Del    Delete current list (will ask for confirmation)

  r, R, e, E, i     Edit (rename list or entry text)

  Enter             Open the selected list (switch to entry view)

ENTRY VIEW SCREEN (Screen 1)
─────────────────────────────────────────────────────────────────────────────
  j, s, Down        Move cursor down (wraps around)
  k, w, Up          Move cursor up (wraps around)
  Home              Jump to first entry
  End               Jump to last entry

  + or a, A         Add a new entry to current list
  d or D            Delete entry at cursor
  Backspace, Del    Delete entry at cursor

  r, R, e, E, i     Edit (rename list or entry text)
  Enter             Edit entry text (in entry view)

  Space             Toggle entry flair (cycle through states)

  Shift + Up        Move entry up in list
  Shift + Down      Move entry down in list

  Tab               Indent entry (add 4 spaces at start)
  Shift+Tab         Unindent entry (remove up to 4 spaces from start)

EDITING SCREEN (When editing entry/list text)
─────────────────────────────────────────────────────────────────────────────
  Left, Right       Move cursor within text
  Ctrl+Left         Move cursor to previous word
  Ctrl+Right        Move cursor to next word
  Backspace         Delete character before cursor
  Delete            Delete character at cursor
  Ctrl+Backspace    Delete entire word before cursor
  Ctrl+Delete       Delete entire word at/after cursor

  Tab               Insert 4 spaces at start of line
  Shift+Tab         Remove up to 4 spaces from start of line

  Enter             Save changes
  Escape, Ctrl+X    Cancel editing (revert changes)

═════════════════════════════════════════════════════════════════════════════
```