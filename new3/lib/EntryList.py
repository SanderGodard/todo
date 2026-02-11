#!/bin/python3
from time import time

from .Entry import Entry

class EntryList:
    """Represents a collection of Entry objects (a single todo list)."""
    def __init__(self, parent, name="Todo list"):
        self.name = name
        self.entries = []
        self.parent = parent


    def rename(self, newName):
        """Renames the list."""
        self.name = newName

    def edit(self, newName):
        """Alias for rename, for consistent handling with Entry.edit()."""
        return self.rename(newName)


    def addEntry(self, entry=None):
        """Adds a new Entry object to the list."""
        if entry is None:
            entry = Entry(parent=self) 
        self.entries.append(entry)
        
        
    def move_entry(self, old_index, direction):
        """
        Moves an entry up or down in the list by swapping it with its neighbor.
        direction: -1 for UP, 1 for DOWN.
        """
        new_index = old_index + direction
        
        # Check bounds: ensure both the old index and the new index are valid
        if not (0 <= old_index < len(self.entries) and 0 <= new_index < len(self.entries)):
            return 
            
        # Perform the move by popping and inserting
        entry_to_move = self.entries.pop(old_index)
        self.entries.insert(new_index, entry_to_move)

    
    def getSortKey(self):
        """
        Returns the timestamp of the most recently modified entry in the list.
        Used by TodoParse to sort the list of lists.
        """
        if not self.entries:
            return 0
        return max(e.getTime() for e in self.entries)

    def delete(self):
        """Removes itself from its parent TodoParse object."""
        self.parent.entryLists.remove(self)


    def getEntries(self):
        return self.entries


    def getTitle(self):
        return self.getName()


    def getName(self):
        return self.name


    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"


    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"
