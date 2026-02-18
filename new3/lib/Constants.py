#!/bin/python3
import curses as c

class Keybinds:
    # Navigation
    UP = [c.KEY_UP, 107, 119]       # KEY_UP, k, w
    DOWN = [c.KEY_DOWN, 106, 115]   # KEY_DOWN, j, s
    LEFT = [c.KEY_LEFT, 104]        # KEY_LEFT, h
    RIGHT = [c.KEY_RIGHT, 108]      # KEY_RIGHT, l
    
    # Movement (Shift + Arrow Keys) - Used for reordering items and navigation
    SHIFT_UP = [337, 547]   # Shift + Up
    SHIFT_DOWN = [336, 548] # Shift + Down
    SHIFT_LEFT = [554, 393]  # Shift + Left, Ctrl + Left (in this terminal)
    SHIFT_RIGHT = [569, 402]  # Shift + Right, Ctrl + Right (in this terminal)
    
    # Actions
    ENTER = [c.KEY_ENTER, 10, 13, 15]    # Enter, \r, Ctrl+O
    FLIP = [32]             # Spacebar
    ADD = [97, 65, 43]      # a, A, +
    DELETE_ITEM = [100, 68] # d, D
    RENAME = [114, 82]      # r, R
    EDIT = [101, 69, 105]   # e, E, i

    # System
    QUIT = [113, 81, 120, 88, 24]   # q, Q, x, X, Ctrl+X
    ESCAPE = [27, 24]               # Escape key, Ctrl+X
    
    # Navigation specials
    HOME = [c.KEY_HOME, 262]
    END = [c.KEY_END, 360]
    
    # Standard curses codes
    backspace = [c.KEY_BACKSPACE, 8, 127, 263] # Common codes for backspace
    delete = [c.KEY_DC, 330] # Common codes for delete key
    
    # Legacy/Alternative names for compatibility
    UP_LEGACY = [337, 547]  # Used for movement/reordering in some contexts
    DOWN_LEGACY = [336, 548]
    
    # Ctrl+Arrow keys for word navigation (multiple codes across terminals)
    ctrlleft = [546, 544, 545, 543, 514, 393]  # Various terminal emulators
    ctrlright = [561, 559, 560, 558, 516, 402]  # Various terminal emulators
    
    # Word deletion keys
    ctrl_backspace = [8, 23, 519, 127]  # Ctrl+Backspace, Ctrl+W, and variants
    ctrl_delete = [520, 521, 528, 383]  # Ctrl+Delete and variants


class Flairs:
    tsk = "tsk" # Task (default/active)
    suc = "suc" # Success (done)
    err = "err" # Error/Urgent
    gen = "gen" # General/Info
    inf = "inf" # Information (for list titles/status bars)
    prt = "prt" # Prompt

    # Order is used for cycling through flairs
    order = [tsk, suc, err, gen, inf]


class FlairSymbols:
    # Symbols are padded with spaces for consistent display width
    convert = {
        Flairs.tsk : "[ ] ",
        Flairs.suc : "[+] ",
        Flairs.err : "[x] ",
        Flairs.gen : "[-] ",
        Flairs.inf : "[i] ",
        Flairs.prt : "[_] "
    }
    
    # Use -1 for the background color to achieve transparency/default background
    BG_COLOR = -1 
    
    # Color MAP used for curses init_pair
    COLOR_MAP = {
        Flairs.tsk: c.COLOR_BLUE,
        Flairs.suc: c.COLOR_GREEN,
        Flairs.err: c.COLOR_RED,
        Flairs.gen: c.COLOR_WHITE,
        Flairs.inf: c.COLOR_MAGENTA, # Status bar / List header
        Flairs.prt: c.COLOR_YELLOW,
    }

        
# Dedicated color pair ID for non-flair text body (used to prevent color bleed)
class ColorPairs:
    DEFAULT_TEXT = 7
