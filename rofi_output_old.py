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

	# 3. Argument for action mode (for keybind integration)
	parser.add_argument(
		'-action', '-a',
		type=str,
		choices=['add', 'edit', 'delete', 'flip'],
		help='Specify an action to perform on selected item.'
	)

	# 4. Argument for selected item (for processing rofi selection)
	parser.add_argument(
		'-selected', '-s',
		type=str,
		help='The selected item from rofi output.'
	)

	return parser.parse_args()

def main():
	args = parse_args()

	todo = Todo()
	todo.load()

	if args.mesg:
		print(todo) # Print the Todo object's __repr__
		return

	# Handle action mode
	if args.action and args.selected:
		perform_action(todo, args.action, args.selected)
		return

	# Determine which list to detail
	target_list_name = args.list
	
	for eL in todo.getEntryLists():
		# Print the EntryList summary
		if target_list_name == "" or target_list_name is None:
			print("[ ]", eL, end="|")

		# Check if the current EntryList matches the one specified by "-list"
		if target_list_name and eL.name == target_list_name:
			# Show the entries for the specified list
			for e in eL.getEntries():
				flair_symbol = FlairSymbols.convert.get(e.getFlair(), "[?]")
				print(flair_symbol, e.getText(), end="|")


def perform_action(todo, action, selected):
	"""Perform an action on the selected item."""
	# Parse selected item (assuming format like "[ ] List Name" or "[*] Entry Text")
	if selected.startswith("[ ] "):
		# It's a list
		list_name = selected[4:]
		el = next((e for e in todo.getEntryLists() if str(e) == list_name), None)
		if not el:
			print(f"List '{list_name}' not found")
			return
		if action == 'delete':
			el.delete()
			todo.save()
			print(f"Deleted list '{list_name}'")
		elif action == 'edit':
			new_name = input(f"New name for '{list_name}': ")
			if new_name:
				el.name = new_name
				todo.save()
				print(f"Renamed list to '{new_name}'")
		else:
			print(f"Action '{action}' not supported for lists")
	elif selected.startswith(("[", "[")) and len(selected) > 3:
		# It's an entry
		flair_symbol = selected[:3]
		entry_text = selected[4:]
		# Find the entry
		entry = None
		for el in todo.getEntryLists():
			for e in el.getEntries():
				if FlairSymbols.convert.get(e.getFlair(), "[?]") == flair_symbol and e.getText() == entry_text:
					entry = e
					break
			if entry:
				break
		if not entry:
			print(f"Entry '{selected}' not found")
			return
		if action == 'delete':
			entry.delete()
			todo.save()
			print(f"Deleted entry '{entry_text}'")
		elif action == 'edit':
			new_text = input(f"Edit '{entry_text}': ")
			if new_text:
				entry.edit(new_text)
				todo.save()
				print(f"Edited entry to '{new_text}'")
		elif action == 'flip':
			entry.flip()
			todo.save()
			print(f"Flipped entry flair")
		else:
			print(f"Action '{action}' not supported for entries")
	else:
		print(f"Invalid selection format: '{selected}'")
