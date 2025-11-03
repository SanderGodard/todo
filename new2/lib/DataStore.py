#!/bin/python3
from os import path, mkdir
import json
from time import time # Added for safer fallback time value

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
            # Note: We rely on the App.py to handle ncurses colors, so raw print is simplified here.
            print("Could not find home folder, putting notes in cwd root")
            home = "./"

        # Enforcing the specific path: ~/.todo/storage.json
        confFolder = path.join(home, ".todo/")
        self.storage = path.join(confFolder, storageFileName)

        if not path.exists(self.storage):
            if not path.exists(confFolder):
                try:
                    mkdir(confFolder)
                    print("Made directory: " + confFolder)
                except:
                    print(f"{Flairs.err} Could not create directory")
                    # Fallback to local file
                    self.storage = storageFileName
            # Create a default list if the storage file doesn't exist
            if not path.exists(self.storage):
                # Ensure there is at least one list and one entry initially
                self.addEntryList()
                self.save()


    def addEntryList(self, entrylist=None):
        """Adds a new EntryList object to the main list."""
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
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Handle empty/corrupt file by initializing default
            print(f"Error loading JSON: {e}. Initializing default structure.")
            jsonObject = False

        self.entryLists = []
        if not jsonObject:
            self.addEntryList(EntryList(self))

        for k, v in jsonObject.items():
            eL = EntryList(self, name=k)
            for eDict in v:
                # Use safe dict access with .get() in case schema changes
                text = eDict.get("text", "Default Entry")
                flair = eDict.get("flair", Flairs.tsk)
                # Fallback to current time if getting file time fails
                time_val = eDict.get("time", int(time()))

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
        try:
            with open(self.storage, "w") as file:
                file.write(str(json.dumps(self.jsonify(), indent=4)))
        except IOError as e:
            print(f"{Flairs.err} Could not save data to {self.storage}")


    def getEntryLists(self):
        """Returns the list of EntryLists, sorted by the time of the most recent change."""
        return self.entryLists
        # Sort lists by the most recently modified entry usin
        # return sorted(self.entryLists, key=lambda el: el.getSortKey(), reverse=True)


    def __str__(self):
        return f"{self.__class__.__name__}({self.storage=}, {len(self.entryLists)=})"

    def __repr__(self):
        return f"{self.__class__.__name__}"
