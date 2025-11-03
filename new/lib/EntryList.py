#!/bin/python3
from time import time

from .Entry import Entry

class EntryList:
    """Represents a container for multiple Entry objects (a Todo list)."""
    def __init__(self, parent, name="Todo list"):
        self.name = name
        self.entries = []
        self.parent = parent # TodoParse instance


    def rename(self, newName=None):
        """Renames the entry list."""
        if newName is not None and newName != self.name:
            self.name = newName

    def edit(self, newName=None):
        return self.rename(newName)


    def open(self):
        """Returns the list of entries. Ensures there is at least one entry."""
        if not self.entries:
            self.addEntry()
        return self.entries


    def addEntry(self, entry=None, index=None):
        """Adds a new Entry object to the list."""
        if entry is None:
            # Create a new default Entry if none is provided
            entry = Entry(parent=self) 

        # Set parent for safety
        entry.parent = self 
        
        if index is not None and 0 <= index <= len(self.entries):
            self.entries.insert(index, entry)
        else:
            self.entries.append(entry)


    def delete(self):
        """Removes the entry list from its parent TodoParse instance."""
        if self in self.parent.entryLists:
            self.parent.entryLists.remove(self)
        return


    def getEntries(self):
        # Sort entries to keep completed tasks at the bottom
        # Sorting key: Done status (False comes before True), then Time (Newest last)
        return sorted(self.entries, 
                      key=lambda e: (e.isDone(), e.getTime()),
                      reverse=False) 

    def getName(self):
        return self.name

    def getTitle(self): # Redundancy for easier handling equal to entries
        return self.getName()

    def getSortKey(self):
        """
        Returns a key for sorting entry lists by last edit time.
        """
        if not self.entries:
            return 0
        # Returns the latest time among all entries
        return max(e.getTime() for e in self.entries)

    def __str__(self):
        return f"{self.name} ({len(self.entries)} items)"

    def __repr__(self):
        return f"<{self.__class__.__name__} name='{self.name}' items={len(self.entries)}>"
