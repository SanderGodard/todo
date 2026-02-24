#!/bin/python3
import subprocess
import sys
from os import path, mkdir
from platform import system
import json

from lib.Constants import *
from lib.Entry import *
from lib.EntryList import *


class Todo:
    def __init__(self):
        self.entryLists = []
        self.storage = None

    def createStorage(self):
        if hasattr(self, 'storage') and self.storage:
            return
        storageFileName = "storage.json"
        if system() == "Windows":
            import getpass
            confFolder = 'C:\\Users\\' + getpass.getuser() + '\\todo\\'
            storage = confFolder + storageFileName
        elif system() == "Linux" or system() == "Darwin":
            try:
                home = path.expanduser("~") + "/"
            except:
                print("Could not find home folder")
                sys.exit(1)
            confFolder = home + ".todo/"
            storage = confFolder + storageFileName
        else:
            print("Unsupported OS")
            sys.exit(1)
        if not path.exists(storage):
            if not path.exists(confFolder):
                try:
                    mkdir(confFolder)
                except:
                    print("Could not create directory: " + confFolder)
                    sys.exit(1)
            try:
                with open(storage, "w") as file:
                    self.addEntryList()
                    file.write(json.dumps(self.jsonify(), indent=4))
            except:
                print("Could not create file: " + storage)
                sys.exit(1)
        self.storage = storage

    def addEntryList(self, entrylist=None):
        if entrylist:
            e = entrylist
        else:
            e = EntryList(parent=self)
            e.addEntry()
        self.entryLists.append(e)
        return self.getEntryLists()[-1]

    def load(self):
        self.createStorage()
        try:
            with open(self.storage, "r") as file:
                jsonObject = json.load(file)
        except:
            print(f"Corrupt storage file: {self.storage}")
            sys.exit(1)

        self.entryLists = []
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
            jsonObject[str(eL)] = []
            for e in eL.getEntries():
                jsonObject[str(eL)].append(e.json())
        return jsonObject

    def save(self):
        with open(self.storage, "w") as file:
            file.write(json.dumps(self.jsonify(), indent=4))

    def getEntryLists(self):
        return self.entryLists

    def __repr__(self):
        return f"Todo({len(self.entryLists)} lists)"


def rofi_menu(options, prompt="Select", mesg=""):
    """Display a rofi menu and return the selected option."""
    if not options:
        return None
    
    input_str = "\n".join(options)
    
    cmd = ["rofi", "-dmenu", "-p", prompt, "-i"]
    if mesg:
        cmd.extend(["-mesg", mesg])
    
    try:
        result = subprocess.run(cmd, input=input_str, text=True, capture_output=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    except FileNotFoundError:
        print("Error: rofi not installed")
        sys.exit(1)


def main():
    todo = Todo()
    todo.load()
    
    current_list = None
    
    while True:
        if current_list is None:
            # Main menu: list of lists
            options = ["[Add New List]"]
            for el in todo.getEntryLists():
                options.append(f"[ ] {el.name}")
            
            mesg = f"Todo: {len(todo.getEntryLists())} lists"
            selection = rofi_menu(options, "Todo Lists", mesg)
            
            if not selection:
                break
            elif selection == "[Add New List]":
                new_name = rofi_menu([""], "New List Name")
                if new_name and new_name.strip():
                    todo.addEntryList(EntryList(todo, name=new_name.strip()))
                    todo.save()
            else:
                list_name = selection[4:]  # Remove "[ ] "
                current_list = next((el for el in todo.getEntryLists() if el.name == list_name), None)
        else:
            # List menu: entries in current list
            options = ["[Back to Lists]", "[Add New Entry]"]
            for e in current_list.getEntries():
                flair_symbol = FlairSymbols.convert.get(e.getFlair(), "[?]")
                options.append(f"{flair_symbol} {e.getText()}")
            
            mesg = f"List: {current_list.name} ({len(current_list.getEntries())} entries)"
            selection = rofi_menu(options, f"Entries in {current_list.name}", mesg)
            
            if not selection:
                break
            elif selection == "[Back to Lists]":
                current_list = None
            elif selection == "[Add New Entry]":
                new_text = rofi_menu([""], "New Entry Text")
                if new_text and new_text.strip():
                    current_list.addEntry(Entry(current_list, text=new_text.strip()))
                    todo.save()
            else:
                # Entry selected, show actions
                flair_symbol = selection[:3]
                entry_text = selection[4:]
                entry = next((e for e in current_list.getEntries() 
                             if FlairSymbols.convert.get(e.getFlair(), "[?]") == flair_symbol 
                             and e.getText() == entry_text), None)
                
                if entry:
                    action_options = ["Edit", "Delete", "Flip Flair", "Cancel"]
                    action = rofi_menu(action_options, f"Action for: {entry_text}")
                    
                    if action == "Edit":
                        new_text = rofi_menu([entry.getText()], "Edit Entry")
                        if new_text and new_text.strip() and new_text != entry.getText():
                            entry.edit(new_text.strip())
                            todo.save()
                    elif action == "Delete":
                        confirm = rofi_menu(["No", "Yes"], "Confirm Delete", f"Delete '{entry_text}'?")
                        if confirm == "Yes":
                            entry.delete()
                            todo.save()
                    elif action == "Flip Flair":
                        entry.flip()
                        todo.save()


if __name__ == "__main__":
    main()