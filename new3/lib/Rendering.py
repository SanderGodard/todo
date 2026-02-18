#!/bin/python3
import curses as c
from .Constants import Flairs, FlairSymbols, ColorPairs

class Rendering:
    """
    Handles all visual output to the ncurses window based on App state.
    (Previously Listview.py)
    """
    def __init__(self, app):
        self.app = app
        self.window = app.window
        

    def draw(self, items, cursor_y, scroll_y, scroll_x, is_editing):
        """
        Draws the main list, applying appropriate flair, colors, and handling scrolling.
        """
        self.window.clear()
        max_y, max_x = self.window.getmaxyx()
        display_height = max_y - 1 # Reserve bottom row for status/edit
        
        # --- Draw List Items ---
        for list_index in range(display_height):
            abs_index = list_index + scroll_y
            
            if abs_index < len(items):
                item_data = items[abs_index]
                item = item_data['data']
                item_type = item_data['type']
                
                is_selected = (abs_index == cursor_y)
                
                row_attr = c.A_NORMAL
                
                # Default text color for the body of the entry/list name
                text_color_pair = c.color_pair(ColorPairs.DEFAULT_TEXT) 
                
                # 1. Determine Flair/Symbol and Text
                if item_type == 'list':
                    flair = Flairs.inf
                    flair_symbol = FlairSymbols.convert.get(flair, FlairSymbols.convert[Flairs.inf])
                    text = f"{item.getTitle()}"
                    flair_color_pair = c.color_pair(FlairSymbols.COLOR_MAP.get(flair, c.COLOR_MAGENTA))
                
                else: # item_type == 'entry'
                    flair = item.getFlair()
                    flair_symbol = FlairSymbols.convert.get(flair, FlairSymbols.convert[Flairs.prt])
                    text = f"{item.getTitle()}"
                    flair_color_pair = c.color_pair(FlairSymbols.COLOR_MAP.get(flair, c.COLOR_RED))


                # --- NEW LOGIC FOR SELECTION AND EDIT MODE ---
                
                # If selected, reverse only the flair, but keep the text normal.
                # If in edit mode AND selected, use the PRT flair color for the flair.
                if is_selected and is_editing:
                    # When editing, flair should use the PRT color for visibility
                    flair_color_pair = c.color_pair(FlairSymbols.COLOR_MAP[Flairs.prt])
                    flair_attr = c.A_BOLD # Add boldness to flair in edit mode
                elif is_selected:
                    # When selected, only the flair is reversed, text remains normal color
                    flair_attr = c.A_REVERSE
                else:
                    flair_attr = c.A_NORMAL


                # 2. Prepare combined line for background drawing
                full_line_content = flair_symbol + text
                
                # 3. Handle Horizontal Scrolling (scroll_x)
                
                # Determine where the flair symbol ends and the text begins
                flair_len = len(flair_symbol)
                
                # The entire line is drawn from column 0
                draw_start_col = 0
                
                # Apply the flair's color pair and attributes to the entire line for drawing flair
                # The background color is transparent, so this only sets the foreground
                # and attributes like A_REVERSE/A_BOLD where needed.
                
                # --- DRAW FLAIR (Symbol) ---
                if flair_len > scroll_x:
                    display_flair = flair_symbol[scroll_x:]
                    flair_draw_len = len(display_flair)
                    self.window.attrset(flair_color_pair | flair_attr)
                    self.window.addstr(list_index, draw_start_col, display_flair)
                    text_draw_start_col = draw_start_col + flair_draw_len
                else:
                    # Flair is completely scrolled off-screen
                    flair_draw_len = 0
                    text_draw_start_col = draw_start_col
                    
                
                # --- DRAW TEXT (Entry/List Name) ---
                text_start_index = max(0, scroll_x - flair_len)
                display_text = text[text_start_index:]
                
                # Calculate max draw length for text (what's left on screen)
                max_draw_len = max_x - text_draw_start_col
                
                # Truncate to fit screen
                display_text_for_color = display_text[:max_draw_len]
                
                # Pad the rest of the line with spaces, using the text_color_pair (which has a transparent BG)
                # The background will be black/transparent unless we explicitly set a reverse attribute.
                
                # If selected but NOT editing, the text should be default color with NO reverse
                final_text_attr = text_color_pair | c.A_NORMAL
                
                self.window.attrset(final_text_attr)
                self.window.addstr(list_index, text_draw_start_col, display_text_for_color)
                
                # Fill the rest of the line with spaces in case the text was short
                fill_len = max_x - text_draw_start_col - len(display_text_for_color)
                if fill_len > 0:
                    # If the text is short, fill the remaining space to the right edge with normal attributes
                    self.window.addstr(" " * fill_len)


        
        # --- Draw Status Bar ---
        status_text = self._get_status_text(cursor_y, len(items), scroll_y)
        # Use configured status bar color pair (pair id 10) if available
        try:
            status_pair = c.color_pair(10)
        except Exception:
            status_pair = c.A_NORMAL

        self.window.attrset(c.A_NORMAL | status_pair | c.A_REVERSE)
        # Truncate to max_x - 1 and pad to cover the entire line safely
        status_line_content = status_text[:max_x - 1].ljust(max_x - 1)
        self.window.addstr(max_y - 1, 0, status_line_content)

    
    def _get_status_text(self, cursor_y, total_items, scroll_y):
        """Constructs the text for the bottom status bar."""
        app = self.app
        # Prepare context variables for formatting
        if app.currentScreen == 0:
            list_name = "MAIN"
        else:
            list_name = app.chosenEntryList.getName() if app.chosenEntryList else "Unknown"

        storage_file = app.storage_path if app.storage_path else "~/.todo/storage.json"
        position = f"Pos: {cursor_y + 1}/{total_items}, X: {app.scroll_x}"

        keybinds_hint = "-k for help"

        divider = app.config.get('divider', '|')

        # Default status format (can be overridden via config)
        fmt = app.config.get('status_bar_format', " {list} {divider} {position} {divider} {storage_file} ")

        status_line = fmt.format(
            divider=divider,
            list=list_name,
            storage_file=storage_file,
            keybinds=keybinds_hint,
            position=position
        )

        return status_line
