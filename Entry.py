#!/bin/python3
from time import time

class Entry:
    def __init__(self, text="New entry :)", flair=Flairs.tsk, time=int(time())):
        self.text = text
        self.flair = flair
        self.time = time


    def edit(newText=self.text):
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


    def getFlair(self):
        return self.flair

    def getText(self):
        return self.text

    def getTime(self):
        return self.time


    def __repr__():
        return f"Entry({text=}, {flair=}, {time=})"
