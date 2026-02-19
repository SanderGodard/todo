#!/bin/python3
from os import path, mkdir
from platform import system
import json
import argparse

from lib.Constants import *
from lib.Entry import *
from lib.EntryList import *


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

## New function for argument parsing
def parse_args():
	"""Configures and runs the argument parser."""
	parser = argparse.ArgumentParser(description="A simple command-line todo application.")

	# 1. Argument for displaying the Todo object's __repr__
	parser.add_argument(
		'-mesg', '-m',
		action='store_true',
		help='Display the full Todo object representation before listing entries.'
	)

	# 2. Argument for listing entries of a specific list
	parser.add_argument(
		'-list', '-l',
		type=str,
		metavar='<EntryList Name>',
		help='Specify the name of an EntryList whose entries should be displayed.'
	)

	return parser.parse_args()

def main():
	args = parse_args()

	todo = Todo()
	todo.load()

	if args.mesg:
		print(todo) # Print the Todo object's __repr__
		exit()
	# Determine which list to detail
	target_list_name = args.list
	
	for eL in todo.getEntryLists():
		# Print the EntryList summary
		# Note: I'm assuming the desired output format is '| [ ] List Name'
		if target_list_name == "":
			print("[ ]", eL, end="|")

		# Check if the current EntryList matches the one specified by "-list"
		# If no list is specified (target_list_name is None), no entries are shown.
		# If a list is specified, only show entries for the matching list.
		if target_list_name and eL.name == target_list_name:
			# Show the entries for the specified list
			for e in eL.getEntries():
				# Note: Assuming 'e.flair' is an index into FlairSymbols.convert
				flair_symbol = FlairSymbols.convert.get(e.getFlair(), "[?]") # Use .get for safety
				print(flair_symbol, e.getText(), end="|")


	# Only show EntryLists normally
#    for eL in todo.getEntryLists():
 #       print("|", "[ ]", eL, end="")
		# if current eL is the "-list <eL>" in args, show its entries
  #      for e in eL.getEntries():
   #         print("|",FlairSymbols.convert[e.flair], e, end="")




if __name__ == "__main__":
    main()
