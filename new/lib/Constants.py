#!/bin/python3


class Keybinds:
    # Navigation
    UP = [259, 107]  # KEY_UP, k
    DOWN = [258, 106] # KEY_DOWN, j
    LEFT = [260, 104] # KEY_LEFT, h
    RIGHT = [261, 108] # KEY_RIGHT, l
    
    # Actions
    ENTER = [10, 13, 15] # Enter, \r, Ctrl+O
    FLIP = [32] # Spacebar
    ADD = [97, 65] # a, A
    DELETE_ITEM = [100, 68] # d, D
    RENAME = [110, 78] # n, N
    EDIT = [101, 69] # e, E

    # System
    QUIT = [113, 81, 120, 88, 24] # q, Q, x, X, Ctrl+X
    ESCAPE = [27] # Escape key


class Flairs:
    tsk = "tsk" # Task (default/active)
    suc = "suc" # Success (done)
    err = "err" # Error/Urgent
    gen = "gen" # General/Info
    inf = "inf" # Information (for list titles/status bars)
    prt = "prt" # Priority

    # Order is used for cycling through flairs
    order = [tsk, suc, err, gen, prt]


class FlairSymbols:
    convert = {
        Flairs.tsk : "  [ ] ",
        Flairs.suc : "  [+] ",
        Flairs.err : "  [x] ",
        Flairs.gen : "  [-] ",
        Flairs.inf : "  [i] ",
        Flairs.prt : "  [!] "
    }
    
    # Color IDs used for curses init_pair (must be unique integers > 0)
    COLOR_ID = {
        Flairs.tsk: 1,
        Flairs.suc: 2,
        Flairs.err: 3,
        Flairs.gen: 4,
        Flairs.inf: 5, # Status bar / List header
        Flairs.prt: 6,
    }

# We can also add a color pair ID for the non-selected, non-flair text body
class ColorPairs:
    # ID reserved for drawing the main body text (transparent BG, white FG)
    DEFAULT_TEXT = 7
