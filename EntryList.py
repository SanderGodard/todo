#!/bin/python3

class EntryList:
    def __init__(self, name="Todo list"):
        self.name = name
        self.entries = []


    def rename(newName=self.name):
        self.name = newName
        return


    def open(self):
        if self.getEntries() == []:
            self.addEntry()
        return getEntries()


    def addEntry(self, entry=Entry()):
        self.entries.append(entry)
        return self.getEntries()[-1]


    def getEntries(self):
        return self.entries

    def getName(self):
        return self.name


    def __repr__():
        return f"EntryList({name=}, entries={len(entries)})"
