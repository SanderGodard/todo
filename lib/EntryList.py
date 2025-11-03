#!/bin/python3

from lib.Entry import *

class EntryList:
    def __init__(self, parent, name="Todo list"):
        self.name = name
        self.entries = []
        self.parent = parent


    def rename(self, newName=None):
        if newName == None:
            newName = self.name
        self.name = newName

    def edit(self, newName=None):
        return self.rename(newName)


    def open(self):
        if self.getEntries() == []:
            self.addEntry()
        return getEntries()


    def addEntry(self, entry=None):
        if entry == None:
            entry = Entry(parent=self)
        self.entries.append(entry)


    def delete(self):
        # self.parent.entryLists.remove(parent.entryLists.index(self))
        self.parent.entryLists.remove(self)
        return


    def getEntries(self):
        return self.entries

    def getName(self):
        return self.name

    def getText(self): # Redundancy for easier handling equal to entries
        return self.getName()


    def __str__(self):
        return f"{self.__class__.__name__}({self.name=}, {len(self.entries)=}, {self.parent=})"

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"
