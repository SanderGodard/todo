#!/bin/python3
from time import time

from lib.Extras import *

class Entry:
    def __init__(self, parent, text="New entry", flair=Flairs.tsk, time=int(time())):
        self.text = text
        self.flair = flair
        self.time = time
        self.parent = parent


    def edit(self, newText=None):
        if newText == None:
            newText = self.text
        self.text = newText
        

    def flip(self):
        self.flair = reversed(Flairs.order)[reversed(Flairs.order).index(self.flair) - 1] # bruker reversed for da slipper jeg å bry meg om positiv wrapping


    def json(self):
        dic = {}
        dic["flair"] = self.getFlair()
        dic["text"] = self.getText()
        dic["time"] = self.getTime()
        return dic


    def delete(self):
        self.parent.entries.remove(self)
        # parent.entries.remove(parent.entries.index(self))
        return


    def getFlair(self):
        return self.flair

    def getText(self):
        return self.text

    def getTime(self):
        return self.time


    def __str__(self):
        return f"{self.__class__.__name__}({self.text=}, {self.flair=}, {self.time=}, {self.parent=})"

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.time}"

