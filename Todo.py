#!/bin/python3
from os import path, mkdir
import json

from lib.LoadBackend import *
from lib.Extras import *
from lib.Entry import *
from lib.EntryList import *
from lib.App import *


class Todo:
    def __init__(self):
        self.todo = TodoParse()
        self.app = App()

        todo.load()

        self.app.start(todo)

    def __str__(self):
        return f"{self.__class__.__name__}({self.storage=}, {len(self.entryLists)=})"

    def __repr__(self):
        return f"{self.__class__.__name__}"


def main():
    todo = Todo()

    print(todo)
    for eL in todo.getEntryLists():
        print("\t", eL)
        print("last edited:", max(eL.getEntries(), key=lambda entry: entry.getTime()).getTime() )
        for e in eL.getEntries():
            print("\t\t", e)




if __name__ == "__main__":
    main()
