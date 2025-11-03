#!/bin/python3
import curses as c

from .Constants import Flairs, FlairSymbols, ColorPairs
from .Entry import Entry
from .EntryList import EntryList

class Rendering:
    """
    Handles the rendering logic for the ncurses interface.
    It draws the current flat list of items (EntryList or Entry objects).
    """
    def __init__(self, app_instance):
        self.app = app_instance
        self.window = app_instance.window

    def draw(self, flat_items, cursor_y, scroll_y, scroll_x):
        """
        Draws the items onto the ncurses window, respecting the scroll and cursor state.
        :param flat_items: A list of dicts, where each dict has 'type' and 'data'.
        :param cursor_y: The index of the currently selected item.
        :param scroll_y: The top row index of the item being displayed.
        :param scroll_x: The horizontal scroll offset.
        """
        max_y, max_x = self.window.getmaxyx()
        display_height = max_y - 1 
        
        self.window.clear()

        visible_items = flat_items[scroll_y : scroll_y + display_height]

        default_text_color_pair = c.color_pair(ColorPairs.DEFAULT_TEXT)

        for list_index, item_wrapper in enumerate(visible_items):
            item = item_wrapper['data']
            item_type = item_wrapper['type']
            
            global_index = scroll_y + list_index
            is_selected = (global_index == cursor_y)

            # --- Determine Text, Symbol, and Colors ---
            
            if item_type == 'list':
                flair_key = Flairs.inf
                text = f"{item.getTitle()} ({len(item.getEntries())} items)"
            elif item_type == 'entry':
                flair_key = item.getFlair()
                text = item.getTitle()
            else:
                flair_key = Flairs.err
                text = "[Unknown Item Type]"

            symbol = FlairSymbols.convert.get(flair_key, "  [?] ")
            
             = FlairSymbols.COLOR_ID.get(flair_key, 1) 
            flair_color_pair = c.color_pair(flair_color_id)

            # --- Apply Attributes ---
            
            # The base attribute (transparent background)
            base_attr = default_text_color_pair 
            
            # If selected, add the reverse attribute to the base
            if is_selected:
                base_attr |= c.A_REVERSE 

            # --- Drawing Logic (Fixes Color Bleed) ---
            
            line_y = list_index
            current_x = 0
            
            # 1. Clear line first with the selection attribute (if active) to ensure transparent background on whole line
            # Instead of clearing the whole line, we rely on the next calls to overwrite/pad
            
            # Determine the flair slice based on scroll_x
            if scroll_x < len(symbol):
                symbol_slice = symbol[scroll_x:]
                flair_attr = flair_color_pair | base_attr
                
                # Draw the flair symbol with its specific color
                try:
                    self.window.addstr(line_y, current_x, symbol_slice, flair_attr)
                    current_x += len(symbol_slice)
                except c.error:
                    pass

            # 2. Draw the Main Text Body
            
            # The text slice calculation ensures we start the text where the symbol slice left off
            effective_scroll_x = max(0, scroll_x - len(symbol))
            text_slice = text[effective_scroll_x:]
            
            text_attr = base_attr # Uses base_attr (DEFAULT_TEXT color pair, transparent BG)

            try:
                # Calculate how much space is left on the screen for the text
                remaining_width = max_x - current_x
                if remaining_width > 0:
                    # Pad the text slice to fill the rest of the line, which ensures 
                    # the A_REVERSE attribute covers the full width if selected.
                    padded_text = text_slice.ljust(remaining_width)
                    self.window.addstr(line_y, current_x, padded_text[:remaining_width], text_attr)
            except c.error:
                pass
            

        # Draw the command/status bar
        self._draw_status_bar(max_y, max_x, cursor_y, len(flat_items), self.app.currentScreen)


    def _draw_status_bar(self, max_y, max_x, cursor_y, total_items, current_screen):
        """Draws the status/command bar on the bottom line."""
        
        if current_screen == 0:
            view_name = "LISTS"
            commands = "(A)dd, (D)elete, (E/N)ame, (J/K/H/L) nav, (->/Enter) Open, (Q/X)uit"
        else:
            view_name = "ENTRIES"
            commands = "(A)dd, (D)elete, (E)dit, (Space) Flip, (J/K/H/L) nav, (<-) Back, (Q/X)uit"

        status_text = f"[{view_name}] Line {cursor_y + 1}/{total_items} | {commands}"
        
        status_color = c.color_pair(FlairSymbols.COLOR_ID.get(Flairs.inf, 5)) | c.A_BOLD
        
        self.window.move(max_y - 1, 0)
        self.window.clrtoeol()
        
        try:
            display_text = status_text.ljust(max_x)[:max_x]
            self.window.addstr(max_y - 1, 0, display_text, status_color)
        except c.error:
            pass
