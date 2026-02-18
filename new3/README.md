# Todo Application - new3 Refactoring Notes

## Overview
This is a refactored version of the original `todo.py` monolithic script, broken down into modular components following the MVC pattern.

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

## Key Improvements

1. **Modular Structure** - Code is organized by responsibility, making it easier to maintain and extend
2. **Status Bar** - Added a bottom status bar showing position, scrolling info, and context-sensitive instructions
3. **Better State Management** - Centralized state in the App class
4. **Separate Data and UI** - DataStore handles persistence, App/Rendering handle UI
5. **Class-Based Design** - Using OOP principles for better code organization

## Kept As-Is
- **Extras/Constants Classes** - The Keybinds, Flairs, FlairSymbols classes from the original Extras.py are preserved in Constants.py
- **TodoParse Class** - The data storage and loading logic remains mostly unchanged
- **Key Navigation** - All original keybindings are maintained

## New Features
- **Status Bar at Bottom** - Shows current position, scroll info, and context-sensitive help
- **Two-Screen Architecture** - Screen 0 for list selection, Screen 1 for entries
- **Color Pair Management** - Dedicated color pair system for better UI consistency
- **Resize Handling** - Application adapts to terminal resize events

## Running the Application

```bash
python3 new3/Todo.py
```

## File Organization Comparison

### Original (todo.py - monolithic)
- 1100+ lines in a single file
- Mixed concerns (UI, business logic, data storage)
- Hard to test individual components

### Refactored (new3/ structure)
```
new3/
├── Todo.py (entry point)
└── lib/
    ├── App.py (controller)
    ├── Constants.py (configuration)
    ├── DataStore.py (data persistence)
    ├── Entry.py (model)
    ├── EntryList.py (model)
    ├── Rendering.py (view)
    └── __init__.py
```

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