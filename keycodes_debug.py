#!/usr/bin/env python3
"""
Key Code Debugger - Shows the actual key codes your terminal sends for any key press.
Run this to identify which codes your terminal sends for Ctrl+Arrow, Home, End, etc.
"""

import curses
import sys


def main(stdscr):
    # Setup curses
    stdscr.keypad(True)
    curses.curs_set(0)
    curses.noecho()
    stdscr.nodelay(False)
    
    # Setup colors
    try:
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_YELLOW, -1)
        curses.init_pair(3, curses.COLOR_CYAN, -1)
    except Exception:
        pass
    
    max_y, max_x = stdscr.getmaxyx()
    line = 0
    keys_pressed = []
    
    while True:
        stdscr.clear()
        
        # Header
        stdscr.addstr(0, 0, "═" * max_x, curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(1, 0, "KEY CODE DEBUGGER - Press any key to see its code (q to quit)", 
                     curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(2, 0, "═" * max_x, curses.color_pair(1) | curses.A_BOLD)
        
        # Instructions
        stdscr.addstr(4, 0, "Try pressing:", curses.color_pair(2))
        instructions = [
            "  • Ctrl+Left / Ctrl+Right - Word navigation",
            "  • Ctrl+Backspace / Ctrl+Delete - Word deletion",
            "  • Home / End - Jump to start/end",
            "  • Tab / Shift+Tab - Indentation",
            "  • Arrow keys with Ctrl/Shift modifiers",
            "  • Any other key combination",
            "",
            "Recent key presses:"
        ]
        
        for i, instr in enumerate(instructions):
            stdscr.addstr(5 + i, 0, instr, curses.color_pair(3) if "Recent" in instr else curses.A_NORMAL)
        
        # Show last 10 key presses
        start_y = 13
        for i, (key_code, key_name) in enumerate(keys_pressed[-10:]):
            line_y = start_y + i
            if line_y < max_y - 2:
                display_text = f"  Code: {key_code:4d}  |  {key_name}"
                stdscr.addstr(line_y, 0, display_text, curses.color_pair(2))
        
        # Footer
        footer_y = max_y - 1
        stdscr.addstr(footer_y, 0, "Press 'q' to quit", curses.A_DIM)
        
        stdscr.refresh()
        
        # Get key
        try:
            key = stdscr.getch()
        except KeyboardInterrupt:
            break
        
        if key == ord('q') or key == ord('Q'):
            break
        
        # Try to get a friendly name for the key
        key_name = _get_key_name(key)
        keys_pressed.append((key, key_name))


def _get_key_name(key):
    """Convert key code to a human-readable name."""
    special_keys = {
        -1: "ERR (no input)",
        9: "Tab",
        10: "Enter",
        13: "Enter (Alt)",
        27: "Escape",
        32: "Space",
        127: "Backspace",
        262: "Home",
        260: "Left",
        261: "Right",
        259: "Up",
        258: "Down",
        330: "Delete",
        336: "Shift+Down",
        337: "Shift+Up",
        360: "End",
        361: "PageUp",
        362: "PageDown",
        514: "Ctrl+Left",
        516: "Ctrl+Right",
        519: "Ctrl+Backspace",
        520: "Ctrl+Delete",
        543: "Ctrl+Left (Alt1)",
        544: "Ctrl+Left (Alt2)",
        545: "Ctrl+Left (Alt3)",
        546: "Ctrl+Left (Alt4)",
        558: "Ctrl+Right (Alt1)",
        559: "Ctrl+Right (Alt2)",
        560: "Ctrl+Right (Alt3)",
        561: "Ctrl+Right (Alt4)",
    }
    
    if key in special_keys:
        return special_keys[key]
    
    # Printable ASCII
    if 32 <= key <= 126:
        return f"'{chr(key)}' (ASCII {key})"
    
    return f"Unknown (code {key})"


if __name__ == "__main__":
    try:
        curses.wrapper(main)
        print("\nKey code testing complete!")
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(0)
