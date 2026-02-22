#!/usr/bin/env python3

import curses

def draw_colors(stdscr):
    # Turn off the blinking cursor
    curses.curs_set(0)
    
    # Initialize colors
    curses.start_color()
    curses.use_default_colors()

    # Get terminal dimensions
    height, width = stdscr.getmaxyx()
    
    # Header
    stdscr.addstr(0, 0, f"Supported Color Pairs: {curses.COLOR_PAIRS}", curses.A_BOLD)
    stdscr.addstr(1, 0, "Press any key to exit...", curses.A_DIM)

    # Calculate grid layout
    # We display pairs 1 through COLOR_PAIRS
    for i in range(1, min(curses.COLOR_PAIRS, 256)):
        try:
            # Initialize the pair: Foreground = i, Background = Default (-1)
            curses.init_pair(i, i, -1)
            
            # Simple grid math
            row = (i // 8) + 3
            col = (i % 8) * 12
            
            if row < height - 1:
                stdscr.addstr(row, col, f"Pair {i:3}", curses.color_pair(i))
        except curses.error:
            # Some terminals report more colors than they can actually init
            break

    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(draw_colors)