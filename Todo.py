#!/bin/python3
from os import path, mkdir
from platform import system
import json

from Extras import *
from Entry import *
from EntryList import *


class Todo:
    def __init__(self):
        self.entryLists = []
        self.storage = None


    def createStorage(self):
        if self.storage in locals() and not self.storage == None:
            return
        # Define storage folder and file
        storageFileName = "storage.json"
        if system() == "Windows":
            import getpass
            confFolder = 'C:\\Users\\' + getpass.getuser() + '\\todo\\'
            storage = confFolder + storageFileName
        elif system() == "Linux" or system() == "Darwin":
            try:
                home = path.expanduser("~") + "/"
            except:
                print(err + "Could not find home folder")
                exit()
            confFolder = home + ".todo/"
            storage = confFolder + storageFileName
        else:
            print("can't recognize OS, edit script to fit")
            exit()
        # Now validate that it is accessible
        if not path.exists(storage):
            if not path.exists(confFolder):
                try:
                    mkdir(confFolder)
                    print("Made directory: " + confFolder)
                except:
                    print("Could not create directory: " + confFolder)
                    exit()
            try:
                with open(storage, "w") as file:
                    self.addEntryList()
                    file.write(str(json.dumps(self.jsonify())))
                print("Made file: " + storage)
            except:
                print("Could not create file: " + storage)
                exit()
        self.storage = storage


    def addEntryList(self, entrylist=False):
        if not entrylist is False:
            e = entrylist
        else:
            e = EntryList(parent=self)
            e.addEntry()
        self.entryLists.append(e)
        return self.getEntryLists()[-1]


    def load(self):
        self.createStorage()
        with open(self.storage, "r") as file:
            try:
                jsonObject = json.load(file)
            except:
                print(f"Try deleting {self.storage}, it may be corrupt")
                exit()

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
        return self.getEntryLists()


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


    def __repr__(self):
        return f"Todo(entryLists={len(self.entryLists)}, {self.storage=})"


def main():
    todo = Todo()
    todo.load()
    print(todo)
    for eL in todo.getEntryLists():
        print("   ", eL)
        for e in eL.getEntries():
            print("     ", e)




if __name__ == "__main__":
    main()
