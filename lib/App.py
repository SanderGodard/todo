#!/bin/python3
import curses as c
import os
import signal
import datetime
from os import path

# Updated imports
from .Constants import Keybinds, Flairs, FlairSymbols, ColorPairs
from .Entry import Entry
from .EntryList import EntryList
from .Rendering import Rendering


class App:
    """
    Main controller for the ncurses UI. Manages state, handles input,
    and orchestrates rendering via Rendering.
    """
    def __init__(self, stdscr, storage_path=None):
        # curses window object
        self.window = stdscr
        self.window.keypad(True)
        self.max_y, self.max_x = self.window.getmaxyx()

        # Application state
        self.data_store = None # Set in start()
        self.currentScreen = 0
        self.chosenEntryList = None
        self.storage_path = storage_path
        self._sigint_received = False
        self.config = {}

        # View state
        self.cursor_y = 0
        self.scroll_y = 0
        self.scroll_x = 0
        self.flat_items = []
        self.is_editing = False
        self._needs_redraw = True # Flag to prevent unnecessary redraws (flickering fix)

        self.set_shorter_esc_delay_in_os()
        c.curs_set(0) # Invisible cursor normally
        c.noecho() # Don't echo input

        # Load config before colors so color settings can be applied
        self._load_config()
        self._setup_colors()

        self.listview = Rendering(self)

    def set_shorter_esc_delay_in_os(self):
        """Sets the delay for ESC key to prevent input lag."""
        os.environ.setdefault('ESCDELAY', '25')

    def _load_config(self):
        """Load or create ~/.todo/config as simple KEY=VALUE env-style file."""
        config = {}
        try:
            home = path.expanduser('~') + '/'
        except Exception:
            home = './'
        conf_dir = path.join(home, '.todo')
        conf_file = path.join(conf_dir, 'config')
        # Ensure directory exists
        if not path.exists(conf_dir):
            try:
                os.mkdir(conf_dir)
            except Exception:
                pass

        # If missing, create default config with comments
        if not path.exists(conf_file):
            default = (
                "# ~/.todo/config - simple KEY=VALUE pairs\n"
                "# status_bar_color: color name (black, red, green, yellow, blue, magenta, cyan, white)\n"
                "# divider: string used between status modules\n"
                "# status_bar_format: python format string using {divider}, {list}, {storage_file}, {keybinds}, {position}, {last_edited}\n"
                "# Examples:\n"
                "# status_bar_color=magenta\n"
                "# divider=|\n"
                "# status_bar_format= {list} {divider} {position} {divider} {last_edited} {divider} {storage_file} \n"
            )
            try:
                with open(conf_file, 'w') as fh:
                    fh.write(default)
            except Exception:
                pass

        # Read file
        try:
            with open(conf_file, 'r') as fh:
                for raw in fh.readlines():
                    line = raw.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        k, v = line.split('=', 1)
                        config[k.strip()] = v.strip()
        except Exception:
            pass

        # Apply defaults
        if 'divider' not in config:
            config['divider'] = '|'
        if 'status_bar_format' not in config:
            config['status_bar_format'] = ' {list} {divider} {position} {divider} {last_edited} {divider} {storage_file} '
        if 'status_bar_color' not in config:
            config['status_bar_color'] = 'magenta'

        self.config = config

    def _setup_colors(self):
        """Initialize color pairs for drawing based on FlairSymbols."""
        if c.has_colors():
            c.use_default_colors()
            c.start_color()

            # 1. Initialize pairs for Flairs (used for symbols)
            for flair, color_id in FlairSymbols.COLOR_MAP.items():
                fg_color = FlairSymbols.COLOR_MAP.get(flair, c.COLOR_WHITE)
                c.init_pair(color_id, fg_color, FlairSymbols.BG_COLOR)

            # 2. Initialize a separate pair for main text (transparent BG, standard FG)
            c.init_pair(ColorPairs.DEFAULT_TEXT, c.COLOR_WHITE, FlairSymbols.BG_COLOR)
            # 3. Optionally apply configured status bar color -> use the color value as pair id
            color_name = self.config.get('status_bar_color', 'magenta').lower()
            color_map = {
                'black': c.COLOR_BLACK,
                'red': c.COLOR_RED,
                'green': c.COLOR_GREEN,
                'yellow': c.COLOR_YELLOW,
                'blue': c.COLOR_BLUE,
                'magenta': c.COLOR_MAGENTA,
                'cyan': c.COLOR_CYAN,
                'white': c.COLOR_WHITE,
            }
            status_fg = color_map.get(color_name, c.COLOR_MAGENTA)
            try:
                c.init_pair(status_fg, status_fg, FlairSymbols.BG_COLOR)
            except Exception:
                pass

    def _flatten_data(self):
        """
        Creates the flat list of items to display (lists or entries)
        and recalculates view limits.
        """
        self.flat_items = []

        if self.currentScreen == 0:
            # Use the sorted list from the data store
            for elist in self.data_store.getEntryLists():
                self.flat_items.append({'type': 'list', 'data': elist})

        elif self.currentScreen == 1 and self.chosenEntryList:
            # Entries are displayed in the exact order they are stored in EntryList.
            for entry in self.chosenEntryList.getEntries():
                self.flat_items.append({'type': 'entry', 'data': entry})

        # Clamp cursor and scroll positions
        total_items = len(self.flat_items)
        display_height = self.max_y - 1

        self.cursor_y = min(self.cursor_y, total_items - 1)
        self.cursor_y = max(0, self.cursor_y)

        if self.cursor_y < self.scroll_y:
            self.scroll_y = self.cursor_y
        if self.cursor_y >= self.scroll_y + display_height:
            self.scroll_y = self.cursor_y - display_height + 1

        self.scroll_y = max(0, self.scroll_y)
        self.scroll_x = max(0, self.scroll_x)


    def _get_selected_item(self):
        """Returns the currently selected item object."""
        if 0 <= self.cursor_y < len(self.flat_items):
            return self.flat_items[self.cursor_y]['data']
        return None

    def _get_selected_item_type(self):
        """Returns the type of the currently selected item ('list' or 'entry')."""
        if 0 <= self.cursor_y < len(self.flat_items):
            return self.flat_items[self.cursor_y]['type']
        return None

    def _handle_move(self, key):
        """Handles moving the selected entry up or down in the list using Shift+Arrows."""

        # Only allow reordering entries (Screen 1)
        if self.currentScreen != 1 or self._get_selected_item_type() != 'entry':
            return

        direction = 0
        if key in Keybinds.SHIFT_UP:
            direction = -1
        elif key in Keybinds.SHIFT_DOWN:
            direction = 1
        else:
            return

        if self.chosenEntryList:
            old_index = self.cursor_y

            self.chosenEntryList.move_entry(old_index, direction)

            # Move the cursor along with the item
            if 0 <= self.cursor_y + direction < len(self.flat_items):
                self.cursor_y += direction

            self._flatten_data()
            self._needs_redraw = True

    def _handle_navigation(self, key):
        """Handles cursor movement and scrolling."""
        initial_cursor = self.cursor_y
        # Wrap-around: up from 0 goes to last, down from last goes to 0
        if key in Keybinds.UP:
            if self.cursor_y > 0:
                self.cursor_y -= 1
            else:
                # wrap to bottom
                self.cursor_y = max(0, len(self.flat_items) - 1)

        elif key in Keybinds.DOWN:
            if self.cursor_y < len(self.flat_items) - 1:
                self.cursor_y += 1
            else:
                # wrap to top
                self.cursor_y = 0

        # Home / End quick jumps
        elif key in Keybinds.HOME:
            self.cursor_y = 0
        elif key in Keybinds.END:
            self.cursor_y = max(0, len(self.flat_items) - 1)

        elif key in Keybinds.LEFT:
            self.scroll_x = max(0, self.scroll_x - 4)
        elif key in Keybinds.RIGHT:
            self.scroll_x += 4

        elif key in Keybinds.ctrlleft or key in Keybinds.SHIFT_LEFT:
            item = self._get_selected_item()
            if item:
                text = item.getTitle()
                pos = self.scroll_x - 1
                while pos > 0 and text[pos] != ' ':
                    pos -= 1
                self.scroll_x = max(0, pos)
        elif key in Keybinds.ctrlright or key in Keybinds.SHIFT_RIGHT:
            item = self._get_selected_item()
            if item:
                text = item.getTitle()
                pos = self.scroll_x
                while pos < len(text) and text[pos] != ' ':
                    pos += 1
                if pos < len(text):
                    self.scroll_x = pos + 1  # after the space
                else:
                    self.scroll_x = len(text)

        if initial_cursor != self.cursor_y or key in Keybinds.LEFT or key in Keybinds.RIGHT or key in Keybinds.SHIFT_LEFT or key in Keybinds.SHIFT_RIGHT or key in Keybinds.ctrlleft or key in Keybinds.ctrlright:
            self._flatten_data()
            self._needs_redraw = True

    def _handle_delete(self):
        """Deletes the selected list or entry."""
        item = self._get_selected_item()
        if not item:
            return
        item.delete()

        if self.currentScreen == 0 and not self.data_store.getEntryLists():
            # If all lists are deleted, create a new default one
            self.data_store.addEntryList()

        # If entries go to zero, remain in the current list view (do not auto-exit)

        # Adjust cursor and redraw
        self._flatten_data()
        # If cursor was beyond the new list length, move it to the last item
        self.cursor_y = min(self.cursor_y, len(self.flat_items) - 1)
        self._needs_redraw = True

    def _handle_add(self):
        """Adds a new list or entry."""
        if self.currentScreen == 0:
            self.data_store.addEntryList()
        elif self.currentScreen == 1 and self.chosenEntryList:
            # Insert new entry directly under the cursor
            insert_pos = self.cursor_y + 1
            self.chosenEntryList.addEntry(entry=insert_pos)

        self._flatten_data()
        # place cursor on the newly added entry
        self.cursor_y = min(len(self.flat_items)-1, insert_pos if self.currentScreen==1 else len(self.flat_items)-1)
        self._needs_redraw = True


    def _handle_rename_or_edit(self):
        """Handles in-place text editing."""
        item = self._get_selected_item()
        if not item:
            return

        # Get the screen position of the selected item
        edit_y = self.cursor_y - self.scroll_y

        # 1. Determine the starting column for the editable text
        item_type = self._get_selected_item_type()
        flair_symbol_len = 0

        # Calculate the length of the symbol/flair prefix to find the text start column
        if item_type == 'list':
            flair_symbol = FlairSymbols.convert.get(Flairs.inf, FlairSymbols.convert[Flairs.inf])
            flair_symbol_len = len(flair_symbol) + 1 # +1 for the space after the symbol
        elif item_type == 'entry':
            flair = item.getFlair()
            flair_symbol = FlairSymbols.convert.get(flair, FlairSymbols.convert[Flairs.tsk])
            flair_symbol_len = len(flair_symbol) + 1 # +1 for the space after the symbol

        # The text starts after the symbol, adjusted for horizontal scrolling (scroll_x)
        # edit_x is the screen column where the first editable character appears.
        edit_x = max(0, flair_symbol_len - self.scroll_x)

        # If the start of the text is scrolled off screen, we cannot edit
        if edit_x >= self.max_x - 1:
            return

        initial_text = f" {item.getTitle()}"  # Include leading space for consistent editing position
        new_text = initial_text
        cursor_pos = 1  # Start cursor after the leading space

        # Set up terminal for editing
        self.is_editing = True
        c.curs_set(1) # Visible cursor
        c.echo() # Echo characters to screen
        self.window.nodelay(False) # Wait for input

        while True:
            # 2. Redraw the list line with the current text
            self.window.move(edit_y, 0)

            # Use the correct color/attribute for the *entire* line for the background
            #row_attr = c.A_REVERSE # Always reverse for edit mode visibility
            row_attr = c.A_NORMAL

            # The part of the input line *before* the editable text (Flair symbol)
            #prefix = flair_symbol
            prefix = FlairSymbols.convert[Flairs.prt]

            # Calculate what part of the prefix is visible due to scroll_x
            visible_prefix = prefix[self.scroll_x:]

            # Calculate horizontal scrolling for the text itself
            display_start_col = 0 # Character index in new_text to start displaying

            # Check if the cursor is past the visible screen area for the text
            # We calculate this based on the cursor position relative to the starting column edit_x
            max_text_width = self.max_x - edit_x
            if cursor_pos >= max_text_width:
                # Calculate the scroll offset for the text itself
                display_start_col = cursor_pos - max_text_width + 1

            # The current text content visible, considering horizontal text scroll
            visible_text_content = new_text[display_start_col:]

            # Combine visible prefix and text content
            full_visible_line = visible_prefix + visible_text_content

            # Truncate and pad the full line to ensure safe drawing
            line_to_draw = full_visible_line[:self.max_x - 1].ljust(self.max_x)

            # Draw the line with PRT color for the prefix
            prt_color_pair = c.color_pair(FlairSymbols.COLOR_MAP[Flairs.prt])
            self.window.attrset(prt_color_pair | row_attr)
            self.window.addstr(edit_y, 0, line_to_draw)

            # Move the cursor to the correct position (Screen x position)
            # screen_cursor_x = (start_column of text) + (cursor_pos in text - 1) - (text_scroll_offset)
            screen_cursor_x = edit_x + (cursor_pos - 1 - display_start_col)

            self.window.move(edit_y, min(self.max_x - 1, screen_cursor_x))
            self.window.refresh()

            # 3. Get Input
            key = self.window.getch()

            if key in Keybinds.ESCAPE:
                # Escape reverts changes
                break
            elif key in Keybinds.ENTER:
                # Allow empty entries and lists
                item.edit(new_text.lstrip())  # Strip leading space when saving
                # If editing a list, make sure to reload the lists in case of sorting by name
                if item_type == 'list':
                    self.data_store.getEntryLists()
                break
            elif key in Keybinds.backspace:
                if cursor_pos > 1:  # Prevent removing the leading space
                    new_text = new_text[:cursor_pos-1] + new_text[cursor_pos:]
                    cursor_pos -= 1
            elif key in Keybinds.delete:
                if cursor_pos < len(new_text):
                    new_text = new_text[:cursor_pos] + new_text[cursor_pos+1:]
            elif key in Keybinds.ctrl_backspace:  # Delete word before cursor
                if cursor_pos > 1:
                    word_start = cursor_pos - 1
                    # If we're in a word, skip back to start of word
                    if word_start >= 0 and new_text[word_start] != ' ':
                        while word_start > 0 and new_text[word_start - 1] != ' ':
                            word_start -= 1
                    # Skip any spaces before the word
                    while word_start > 0 and new_text[word_start - 1] == ' ':
                        word_start -= 1
                    new_text = new_text[:word_start] + new_text[cursor_pos:]
                    cursor_pos = max(1, word_start)  # Don't go before the space
            elif key in Keybinds.ctrl_delete:  # Delete word at/after cursor
                if cursor_pos < len(new_text):
                    word_end = cursor_pos
                    # Skip current word
                    while word_end < len(new_text) and new_text[word_end] != ' ':
                        word_end += 1
                    # Skip spaces after word
                    while word_end < len(new_text) and new_text[word_end] == ' ':
                        word_end += 1
                    new_text = new_text[:cursor_pos] + new_text[word_end:]
            elif key in Keybinds.ctrlleft:
                # Move cursor to start of previous word
                if cursor_pos > 1:
                    new_pos = cursor_pos - 1
                    # Skip spaces before cursor
                    while new_pos > 0 and new_text[new_pos] == ' ':
                        new_pos -= 1
                    # Skip word itself to reach its start
                    while new_pos > 0 and new_text[new_pos - 1] != ' ':
                        new_pos -= 1
                    cursor_pos = max(1, new_pos)  # Don't go before the space
            elif key in Keybinds.ctrlright:
                # Move cursor to start of next word
                if cursor_pos < len(new_text):
                    new_pos = cursor_pos
                    # Skip current word
                    while new_pos < len(new_text) and new_text[new_pos] != ' ':
                        new_pos += 1
                    # Skip spaces to reach next word
                    while new_pos < len(new_text) and new_text[new_pos] == ' ':
                        new_pos += 1
                    cursor_pos = new_pos
            elif key == 9:  # Tab: insert 4 spaces at start of line
                new_text = (' ' * 4) + new_text
                cursor_pos += 4
            elif key == c.KEY_BTAB:  # Shift+Tab: remove up to 4 leading spaces
                remove = 0
                for i in range(min(4, len(new_text))):
                    if new_text[i] == ' ':
                        remove += 1
                    else:
                        break
                if remove > 0:
                    new_text = new_text[remove:]
                    cursor_pos = max(1, cursor_pos - remove)  # Don't go before the space
            elif key == c.KEY_LEFT:
                cursor_pos = max(1, cursor_pos - 1)  # Don't go before the space
            elif key == c.KEY_RIGHT:
                cursor_pos = min(len(new_text), cursor_pos + 1)
            elif 32 <= key <= 255: # Printable characters
                char = self.cleanInput(chr(key))
                if char is False:
                    continue
                new_text = new_text[:cursor_pos] + char + new_text[cursor_pos:]
                cursor_pos += 1

        # Restore terminal state
        self.is_editing = False
        c.curs_set(0)
        c.noecho()
        self.window.nodelay(False)  # Return to blocking input
        # Force a full redraw to repaint the line without the reverse attribute
        self._flatten_data()
        self._needs_redraw = True


    def cleanInput(self, inp):
        dict = {165:229, 133:197, 184:248, 152:216, 166:230, 134:198}
        try:
            code = ord(inp)
        except Exception:
            return inp
        if code in dict:
            inp = chr(dict[code])
        elif code == 195: #Ã
            inp = False
        return inp

    def _handle_view_switch(self, key):
        """Handles switching between list selection (0) and entry view (1)."""
        if self.currentScreen == 0:
            item = self._get_selected_item()
            if self._get_selected_item_type() == 'list':
                self.chosenEntryList = item
                self.currentScreen = 1

        elif self.currentScreen == 1:
            self.currentScreen = 0
            self.chosenEntryList = None

        # Reset view state for the new screen
        self.cursor_y = 0
        self.scroll_y = 0
        self.scroll_x = 0
        self._flatten_data()
        self._needs_redraw = True

    def handle_input(self, key):
        """Processes a single keypress event."""
        # Handle item movement (Shift+Up/Down for reordering)
        if key in Keybinds.SHIFT_UP or key in Keybinds.SHIFT_DOWN:
            self._handle_move(key)
            return True

        if key in Keybinds.UP or key in Keybinds.DOWN or key in Keybinds.LEFT or key in Keybinds.RIGHT or key in Keybinds.HOME or key in Keybinds.END or key in Keybinds.ctrlleft or key in Keybinds.ctrlright or key in Keybinds.SHIFT_LEFT or key in Keybinds.SHIFT_RIGHT:
            self._handle_navigation(key)

        if key in Keybinds.ADD:
            self._handle_add()
#            self._handle_rename_or_edit()

        if key in Keybinds.DELETE_ITEM or key in Keybinds.delete or key in Keybinds.backspace:
            self._handle_delete()

        # Allow 'i' to edit in addition to 'e' and 'r'
        if key in Keybinds.RENAME or key in Keybinds.EDIT or key == ord('i') or (self.currentScreen == 1 and key in Keybinds.ENTER):
            self._handle_rename_or_edit()

        # Tab/Shift-Tab outside edit mode: indent/unindent current entry's text
        if key == 9:  # Tab
            if self.currentScreen == 1:
                sel = self._get_selected_item()
                if sel:
                    sel.text = (' ' * 4) + sel.text
                    self._needs_redraw = True
            return True
        if key == c.KEY_BTAB:  # Shift+Tab
            if self.currentScreen == 1:
                sel = self._get_selected_item()
                if sel and sel.text.startswith('    '):
                    sel.text = sel.text[4:]
                    self._needs_redraw = True
            return True

        if self.currentScreen == 0:
            if key in Keybinds.ENTER: # or key in Keybinds.RIGHT:
                self._handle_view_switch(key)

            if key in Keybinds.QUIT or key in Keybinds.ESCAPE:
                return False

        elif self.currentScreen == 1:
            #if key in Keybinds.LEFT:
            #   self._handle_view_switch(key)

            if key in Keybinds.QUIT or key in Keybinds.ESCAPE:
                self._handle_view_switch(key)

            if key in Keybinds.FLIP:
                item = self._get_selected_item()
                if self._get_selected_item_type() == 'entry':
                    item.flip()
                    self._needs_redraw = True

        return True

    # Main Loop
    def start(self, data_store):
        """
        Main application loop. Updates only on keystroke or terminal resize.
        """
        self.data_store = data_store
        self._flatten_data()
        self.window.nodelay(False)  # Blocking input: wait for keystroke

        # Setup SIGINT -> soft close
        def _sigint_handler(signum, frame):
            self._sigint_received = True
        signal.signal(signal.SIGINT, _sigint_handler)

        # Draw initial screen before waiting for input
        self.listview.draw(self.flat_items, self.cursor_y, self.scroll_y, self.scroll_x, self.is_editing)
        self.window.refresh()
        self._needs_redraw = False

        running = True

        while running:
            # 1. Check for terminal resize
            new_max_y, new_max_x = self.window.getmaxyx()
            resize_happened = (new_max_y != self.max_y or new_max_x != self.max_x)
            
            if resize_happened:
                self.max_y, self.max_x = new_max_y, new_max_x
                self._flatten_data()
                self._needs_redraw = True

            # 2. Input - Blocking call waits for keystroke
            key = self.window.getch()

            if key != c.ERR and key != -1:
                running = self.handle_input(key)
                # Input was received, we'll redraw below if needed

            # Check for SIGINT
            if getattr(self, '_sigint_received', False):
                running = False

            # 3. Rendering - Only draw if something has changed or key was pressed
            if self._needs_redraw and not self.is_editing:
                self.listview.draw(self.flat_items, self.cursor_y, self.scroll_y, self.scroll_x, self.is_editing)
                self.window.refresh()
                self._needs_redraw = False

        # Save data when exiting
        self.data_store.save()
