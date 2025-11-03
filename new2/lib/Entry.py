#!/bin/python3
from time import time

from .Constants import Flairs

class Entry:
    """Represents a single task or item within an EntryList."""
    def __init__(self, parent, text="New entry", flair=Flairs.tsk, time=int(time())):
        self.text = text
        self.flair = flair
        self.time = time
        self.parent = parent


    def edit(self, newText):
        """Edits the text of the entry and updates the timestamp."""
        self.text = newText
        self.time = int(time())


    def flip(self):
        """
        Cycles the flair to the next one in the defined order and updates the timestamp.
        The entry's position in the list is NOT affected.
        """
        # Using standard modulo arithmetic for reliable cycling
        current_index = Flairs.order.index(self.flair)
        next_index = (current_index + 1) % len(Flairs.order)
        self.flair = Flairs.order[next_index]
        self.time = int(time()) # Update timestamp to reflect modification time


    def json(self):
        """Returns a JSON-serializable dictionary representation."""
        return {
            "flair": self.getFlair(),
            "text": self.getText(),
            "time": self.getTime()
        }


    def delete(self):
        """Removes itself from its parent EntryList."""
        self.parent.entries.remove(self)


    def getFlair(self):
        return self.flair

    def getText(self):
        return self.text
    
    def getTitle(self): # Alias for consistency with EntryList/Rendering
        return self.getText() 

    def getTime(self):
        return self.time


    def __str__(self):
        return f"{self.__class__.__name__}({self.text=}, {self.flair=}, {self.time=})"

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.time}"
