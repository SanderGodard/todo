#!/bin/python3
from time import time

from Extras import *

class Entry:
    def __init__(self, parent, text="New entry :)", flair=Flairs.tsk, time=int(time())):
        self.text = text
        self.flair = flair
        self.time = time
        self.parent = parent


    def edit(newText=None):
        if newText == None:
            newText = self.text
        self.text = newText
        return


    def flip(self):
        self.flair = reversed(Flairs.order)[reversed(Flairs.order).index(self.flair) - 1] # bruker reversed for da slipper jeg å bry meg om positiv wrapping


    def json(self):
        dic = {}
        dic["flair"] = self.getFlair()
        dic["text"] = self.getText()
        dic["time"] = self.getTime()
        return dic


    def delete(self):
        parent.entries.remove(parent.entries.index(self))
        return


    def getFlair(self):
        return self.flair

    def getText(self):
        return self.text

    def getTime(self):
        return self.time


    def __repr__(self):
        return f"Entry({self.text=}, {self.flair=}, {self.time=})"
