#!/bin/python3
from os import path, mkdir
import json

from lib.Extras import *
from lib.Entry import *
from lib.EntryList import *


class TodoParse:
    def __init__(self):
        self.entryLists = []
        self.storage = None


    def validateStorage(self):
        if self.storage in locals() and not self.storage == None: # Already is set
            return
        # Define storage folder and file
        storageFileName = "storage.json"
        try:
            home = path.expanduser("~") + "/"
        except:
            print(Flairs.err + "Could not find home folder, putting in root")
            home = "/"

        confFolder = home + ".todo/"
        self.storage = confFolder + storageFileName

        # Now validate that it is accessible
        if not path.exists(self.storage):
            if not path.exists(confFolder):
                mkdir(confFolder)
                print("Made directory: " + confFolder)
            self.addEntryList()
            self.save()


    def addEntryList(self, entrylist=False):
        if not entrylist is False:
            e = entrylist
        else:
            e = EntryList(parent=self)
            e.addEntry()
        self.entryLists.append(e)


    def load(self):
        self.validateStorage()
        with open(self.storage, "r") as file:
            jsonObject = json.load(file)

        if len(str(jsonObject)) < 3:
            self.addEntryList()
            jsonObject = self.jsonify()

        self.entryLists = [] # Start with clean slate, then generate objects based on the JSON
        for k, v in jsonObject.items():
            eL = EntryList(self, name=k)
            for eDict in v:
                e = Entry(eL, text=eDict["text"], flair=eDict["flair"], time=eDict["time"])
                eL.addEntry(e)
            self.addEntryList(eL)


    def jsonify(self):
        jsonObject = {}
        for eL in self.getEntryLists():
            jsonObject[eL] = []
            for l in eL.getEntries():
                jsonObject[eL].append(l.jsonify())
        return jsonObject


    def save(self):
        with open(self.storage, "w") as file:
            file.write(str(json.dumps(self.jsonify(), indent=4)))


    def getEntryLists(self):
        return self.entryLists


    def __str__(self):
        return f"{self.__class__.__name__}({self.storage=}, {len(self.entryLists)=})"

    def __repr__(self):
        return f"{self.__class__.__name__}"


def main():
    todo = TodoParse()
    todo.load()
    print(todo)
    for eL in todo.getEntryLists():
        print("\t", eL)
        print("last edited:", max(eL.getEntries(), key=lambda entry: entry.getTime()).getTime() )
        for e in eL.getEntries():
            print("\t\t", e)




if __name__ == "__main__":
    main()
