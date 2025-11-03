#!/bin/python3
from os import path, mkdir
import json

from .Constants import Flairs # Renamed from Extras
from .Entry import Entry
from .EntryList import EntryList


class TodoParse:
    """Handles loading, saving, and managing the main collection of EntryLists."""
    def __init__(self):
        self.entryLists = []
        self.storage = None


    def validateStorage(self):
        """Sets the storage path and creates the file/directory if it doesn't exist."""
        if self.storage is not None:
            return
        
        storageFileName = "storage.json"
        
        try:
            home = path.expanduser("~") + "/"
        except:
            print(Flairs.err + "Could not find home folder, putting in root")
            home = "/"

        confFolder = path.join(home, ".todo/")
        self.storage = path.join(confFolder, storageFileName)

        if not path.exists(self.storage):
            if not path.exists(confFolder):
                mkdir(confFolder)
                print("Made directory: " + confFolder)
            # Ensure there is at least one list and one entry initially
            self.addEntryList() 
            self.save()


    def addEntryList(self, entrylist=None):
        """Adds a new EntryList object."""
        if entrylist is None:
            e = EntryList(parent=self)
            e.addEntry()
        else:
            e = entrylist
        self.entryLists.append(e)


    def load(self):
        """Loads data from the JSON storage file."""
        self.validateStorage()
        try:
            with open(self.storage, "r") as file:
                jsonObject = json.load(file)
        except Exception as e:
            # Handle empty/corrupt file by initializing default
            print(f"Error loading JSON: {e}. Initializing default structure.")
            self.entryLists = []
            self.addEntryList()
            return

        if not jsonObject:
            self.entryLists = []
            self.addEntryList()
            return

        self.entryLists = []
        for k, v in jsonObject.items():
            eL = EntryList(self, name=k)
            for eDict in v:
                # Use safe dict access with .get() in case schema changes
                text = eDict.get("text", "Default Entry")
                flair = eDict.get("flair", Flairs.tsk)
                time_val = eDict.get("time", int(path.getmtime(self.storage)))
                
                e = Entry(eL, text=text, flair=flair, time=time_val)
                eL.addEntry(e)
            self.entryLists.append(eL)


    def jsonify(self):
        """Converts internal objects to a JSON-serializable dictionary."""
        jsonObject = {}
        for eL in self.getEntryLists():
            jsonObject[eL.getName()] = [l.json() for l in eL.getEntries()]
        return jsonObject


    def save(self):
        """Saves the current state to the JSON storage file."""
        self.validateStorage()
        with open(self.storage, "w") as file:
            file.write(str(json.dumps(self.jsonify(), indent=4)))


    def getEntryLists(self):
        return self.entryLists

    def __str__(self):
        return f"{self.__class__.__name__}({self.storage=}, {len(self.entryLists)=})"

    def __repr__(self):
        return f"{self.__class__.__name__}"
