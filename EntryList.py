#!/bin/python3

from Entry import *

class EntryList:
    def __init__(self, parent, name="Todo list"):
        self.name = name
        self.entries = []
        self.parent = parent


    def rename(newName=None):
        if newName == None:
            newName = self.name
        self.name = newName
        return


    def open(self):
        if self.getEntries() == []:
            self.addEntry()
        return getEntries()


    def addEntry(self, entry=None):
        if entry == None:
            entry = Entry(parent=self)
        self.entries.append(entry)
        return self.getEntries()[-1]


    def delete(self):
        parent.entryLists.remove(parent.entryLists.index(self))
        return


    def getEntries(self):
        return self.entries

    def getName(self):
        return self.name

    def getText(self):
        return self.getName()


    def __repr__(self):
        return f"EntryList({self.name=}, entries={len(self.entries)})"
