#!/bin/python3
from time import time
import sys
# Added import for time used in load/save and initialization
from .Constants import Flairs, FlairSymbols

class Entry:
    """Represents a single todo item."""
    def __init__(self, parent, text="New entry", flair=Flairs.tsk, time=int(time())):
        self.title = text
        self.flair = flair
        self.time = time
        self.parent = parent # EntryList instance

    def edit(self, newText=None):
        """Edits the title of the entry and updates the time."""
        if newText is not None:
            self.title = newText
        self.time = int(time())
        
    def flip(self):
        """Cycles through the available flairs (task/done states)."""
        order = Flairs.order
        try:
            current_index = order.index(self.flair)
            # Cycle to the next flair in the order list. The modulo operator handles wrapping.
            next_index = (current_index + 1) % len(order)
            self.flair = order[next_index]
        except ValueError:
            # If the current flair is not in the order list, default to 'tsk'
            self.flair = Flairs.tsk
        self.time = int(time())

    def isDone(self):
        """Convenience method to check if the entry is marked as 'done' (suc)."""
        return self.flair == Flairs.suc
    
    def json(self):
        """Returns a JSON serializable dictionary representation of the entry."""
        dic = {}
        dic["flair"] = self.getFlair()
        dic["text"] = self.getTitle()
        dic["time"] = self.getTime()
        return dic

    def delete(self):
        """Removes the entry from its parent list."""
        if self in self.parent.entries:
            self.parent.entries.remove(self)

    def getFlair(self):
        return self.flair

    def getTitle(self):
        return self.title

    def getTime(self):
        return self.time

    def __str__(self):
        flair_symbol = FlairSymbols.convert.get(self.flair, "[?] ")
        return f"{flair_symbol}{self.title}"

    def __repr__(self):
        return f"<{self.__class__.__name__} title='{self.title[:20]}...' time={self.time}>"
