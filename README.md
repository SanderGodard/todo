# Todo 
Now in **v2.0\***

\* After being vibecoded beyond recognition


Small todo list program written in python 3 using the curses library

## Install
```sh
curl https://raw.githubusercontent.com/SanderGodard/todo/refs/heads/main/install.sh | bash
```

### Manually
```sh
git clone git@github.com:SanderGodard/todo.git
cd todo
sudo ln -s $(pwd)/todo.py /usr/bin/todo
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

#### Find all local storage files
```sh
find / -name '.todolist.json' 2>/dev/null
```

### Config

#### Editable variables
```
status_bar_color=green 
# choose any color of the following
# (black, red, green, yellow, blue, magenta, cyan, white)
divider=;
# Any char
status_bar_format= {list} {divider} {position} {divider}
# Available modules
# {divider}, {list}, {storage_file}, {keybinds}, {position}
```

#### Example
```
# ~/.todo/config - simple KEY=VALUE pairs

# status_bar_color: color name (black, red, green, yellow, blue, magenta, cyan, white)
status_bar_color=white

# divider: string used between status modules
divider=|

# status_bar_format: python format string using {divider}, {list}, {storage_file}, {keybinds}, {position}
status_bar_format= {storage_file} {divider} List: {list} {divider} Pos: {position}
```

## Keybinds
```
╔════════════════════════════════════════════════════════════════════════════╗
║                          TODO APPLICATION KEYBINDS                         ║
╚════════════════════════════════════════════════════════════════════════════╝

COMMON KEYBINDS (All Screens)
─────────────────────────────────────────────────────────────────────────────
  H, Left               Navigate left (horizontal scrolling)
  L, Right              Navigate right (horizontal scrolling)
  J, S, Down            Move cursor down (wraps around)
  K, W, Up              Move cursor up (wraps around)
  Home                  Jump to first list
  End                   Jump to last list

  Q, X, Esc, Ctrl+X     Go back (exit entry view or quit app)

  +, A                  Add a new entry at cursor
  D, Del, Backspace     Delete entry at cursor

  R, E, I, Enter        Edit entry

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

  Tab                   Insert 4 spaces at start of line
  Shift+Tab             Remove up to 4 spaces from start of line

  Enter, Ctrl+O         Save changes
  Esc, Ctrl+X           Cancel editing (revert changes)

═════════════════════════════════════════════════════════════════════════════
```