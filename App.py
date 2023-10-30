#!/bin/python3
from os import path, mkdir, environ
import curses as c
from platform import system
from time import sleep, time
import json

from Todo import *
from Extras import *
from Entry import *
from EntryList import *


class App:
    def __init__(self, stdscr, todo):
        self.stdscr = stdscr
        self.todo = todo

        self.chosenEntryList = False
        # default settings
        self.scrollx = 1
        self.scrolly = 0
        self.editx = 4
        self.xwinscroll = 0
        self.ywinscroll = 0


    def set_shorter_esc_delay_in_os():
        environ.setdefault('ESCDELAY', '25')


    def cleanInp(inp):
        dict = {165:229, 133:197, 184:248, 152:216, 166:230, 134:198}
        if inp in dict:
            inp = dict[inp]
        elif inp == 195: #Ã
            inp = False
        return inp


    def chooseEntryList(self, eL=False):
        self.chosenEntryList = eL


    def alert(self, text):
        self.stdscr.attron(c.color_pair(5))
        text = text[self.xwinscroll:self.stdscr.getmaxyx()[1]+self.xwinscroll-1]
        text = text + " "*int(self.stdscr.getmaxyx()[1] - len(text))
        if len(text) < 1:
            text = " "
        self.wr(text, self.stdscr.getmaxyx()[0]-1, "force")

        self.stdscr.attroff(c.color_pair(5))

        self.stdscr.refresh()
        return


    def resetView(self, todo):
        return


    def prompt(self):
        return


    def helpFunc(self):
        helpstr = """Keys             :   Actions

        h                :   Display this help screen
        r                :   Refresh terminal window

        up, down         :   Scroll vertically in the list
        left, right      :   Scroll horizontally in the list

        shift + up|down  :   Move task in list

        +, a             :   Add task to list on cursor
        backspace, d     :   Delete task from list on cursor
            This will ask for confirmation.
              enter, y, backspace   : Yes
              escape, n, c, q       : No

        enter, e         :   Edit task text
            This will allow you to edit selected task
              enter                 : Save
              escape                : Cancel
        space            :   Switch task 'state' on cursor

        esc, q, x        :   Exit program


        Hotkeys for the list menu:
        +, a             :   Add list
        r                :   Rename list
        backspace, delete:   Delete list"""
        if self.stdscr.getmaxyx()[1] <= 56:
            helpstr = helpstr.replace("    ", " ")
        if self.stdscr.getmaxyx()[0] <= 4:
            helpstr = """Make your terminal
            size larget to read
            all the instructions"""
        self.stdscr.clear()
        for i, line in enumerate(helpstr.splitlines()):
            if i == 0:
                self.wr(line, i, Flairs.inf)
            else:
                self.wr(line, i)

        self.alert("Press any key to exit this menu")

        self.stdscr.move(0, 1)
        self.stdscr.refresh()
        wait = self.stdscr.getch()
        self.resetView()
        return


    def getData(self):
        results = []
        if not self.chosenEntryList is False:
            for e in self.chosenEntryList:
                results.append(e)
        else:
            for l in self.todo.getEntryLists():
                results.append(l)
        return results


    def winrefresh(self, direction=False):
        # self.scrolly
        # self.stdscr
        return


    def scrollup(self):
        if self.stdscr.getyx()[0] <= 0:
            self.winrefresh(self.getData(), "up")
            shifted = True
        else:
            shifted = False

        if not shifted:
            if self.stdscr.getyx()[0] > 0:
                self.stdscr.move(scrolly-1, self.scrollx)
            else:
                self.stdscr.move(0, self.scrollx)
        elif shifted:
            if self.ywinscroll >= len(self.getData())-1-(self.stdscr.getmaxyx()[0]-2):
                if len(self.getData()) == 0:
                    # Put self.stdscr.move(self.stdscr.getmaxyx()[0], self.scrollx) here to remove indent effect on scrollup with empty list
                    pass
                elif len(self.getData())-1 <= (self.stdscr.getmaxyx()[0]-2):
                    self.stdscr.move(len(self.getData())-1, self.scrollx)
                else:
                    self.stdscr.move(self.stdscr.getmaxyx()[0]-2, self.scrollx)
            else:
                self.stdscr.move(0, self.scrollx)
        else:
            self.stdscr.move(0, self.scrollx)
        self.stdscr.refresh()
        return


    def scrolldown(self):
        if self.stdscr.getyx()[0] >= self.stdscr.getmaxyx()[0]-2 or self.ywinscroll+self.stdscr.getyx()[0] >= len(self.getData())-1:
            self.winrefresh(self.getData(), "down")
            shifted = True
        else:
            shifted = False

        if not shifted:
            if self.stdscr.getyx()[0] < (self.stdscr.getmaxyx()[0]-2) or self.ywinscroll+self.stdscr.getyx()[0] <= len(self.getData())-1:
                self.stdscr.move(y+1, self.scrollx)
            else:
                self.stdscr.move(0, self.scrollx)
        elif shifted:
            if ywinscroll <= 0:
                self.stdscr.move(0, self.scrollx)
            else:
                self.stdscr.move(y, self.scrollx)
        else:
            self.stdscr.move(0, self.scrollx)
        self.stdscr.refresh()
        return


    def winrefresh(self, direction="none", y=0):
        if direction == "up":
            if self.ywinscroll <= 0:
                if len(self.getData())-1 <= (self.stdscr.getmaxyx()[0]-2):
                    self.ywinscroll = 0
                else:
                    self.ywinscroll = len(self.getData())-1-(self.stdscr.getmaxyx()[0]-2)
            else:
                self.ywinscroll -= 1

        if direction == "down":
            if self.ywinscroll >= len(self.getData())-(self.stdscr.getmaxyx()[0]-2) or self.ywinscroll+self.stdscr.getyx()[0] >= len(self.getData())-1:
                self.ywinscroll = 0
            else:
                self.ywinscroll += 1

        elif direction == "right" and self.xwinscroll <= 247:
            self.xwinscroll += 8
        elif direction == "left" and self.xwinscroll >= 8:
            self.xwinscroll -= 8

        self.stdscr.clear()
        printData(self.getData(), False)
        self.stdscr.refresh()
        return


    def wr(self, text, row, flair=Flairs.gen, focus=False):
        h, w = self.stdscr.getmaxyx()
        if row >= h-1 or not flair == "force":
            if not flair in ["", "force"]:
                text = text[:w-5]
            else:
                text = text[:w-1]

        try:
            symbol = FlairSymbols.convert[flair]
            colorpair = FlairSymbols.color[flair]
            symbol += " "
        except:
            symbol = ""
            colorpair = FlairSymbols.color[Flairs.gen]

        self.stdscr.attron(c.color_pair(colorpair))
        self.stdscr.addstr(row, 0, symbol)
        self.stdscr.attroff(c.color_pair(colorpair))
        if focus:
            self.stdscr.attron(c.color_pair(FlairSymbols.color[Flairs.gen]))
            self.stdscr.addstr(row, len(symbol), text)
            self.stdscr.attroff(c.color_pair(FlairSymbols.color[Flairs.gen]))
        else:
            self.stdscr.addstr(row, len(symbol), text)
        return


    def printData(self):
        h, w = self.stdscr.getmaxyx()
        entries = self.getData()[self.ywinscroll:self.ywinscroll+self.stdscr.getmaxyx()[0]-1]
        for i, entry in enumerate(entries):
            if self.xwinscroll <= 0: # Account for flairs aka symbols
                plus = 4
                scrolled = False
            else:
                plus = 0
                scrolled = True
                # self.debu(str(entry))
                # self.debu(str(data))
                entryText = entryText.getText()[self.xwinscroll:self.stdscr.getmaxyx()[1]+self.xwinscroll-1]
                if len(entryText) < 1:
                    entryText = entryText + " "
            self.wr(entryText, i, entry.getFlair())
        return


    def resetView(self, y=0):
        self.stdscr.clear()
        self.printData()
        self.stdscr.move(y, self.scrollx)
        self.stdscr.refresh()
        return


    def youSurePrompt(self, y):
        entry = self.getData()[y-self.ywinscroll]
        text = entry.getText()[self.xwinscroll:self.stdscr.getmaxyx()[1]+self.xwinscroll-1]
        self.wr(text, y, Flairs.prt)

        self.alert("Do you want to delete this entry? (Y/n) ")

        cont = True
        while cont:
            accept = self.stdscr.getch()
            accept = self.cleanInp(accept)
            if accept in Keybinds.enter or accept in [121, 89] or accept in Keybinds.backspace or accept in Keybinds.delete: #enter, y, backspace
                entry.delete()
                cont = False
            elif accept in [110, 780, 27, 990, 670, 81, 113]: #n, esc, c, q
                cont = False

        self.resetView(y-self.ywinscroll)
        return


    def deleteListName(self, y): # Accesser før man velger liste
        entryList = self.getData()[y]
        text = entryList.getName()
        self.wr(text, y, Flairs.prt)

        self.alert("Do you want to delete this list? (Y/n) ")

        cont = True
        while cont:
            accept = self.stdscr.getch()
            accept = self.cleanInp(accept)
            if accept in Keybinds.enter or accept in [121, 89] or accept in Keybinds.backspace or accept in Keybinds.delete: #enter, y, backspace
                entryList.delete()
                cont = False
            elif accept in [110, 780, 27, 990, 670, 81, 113]: #n, esc, c, q
                cont = False

        self.resetView(y)
        return


    def __repr__(self):
        return f"App({stdscr=})"



def makeNew(stdscr, data, y=0, y2=0):
    #if len(data) == 0:
        #alert(stdscr, str(data))
        #stdscr.refresh()
        #stdscr.getch()
        #data.append({})
        #alert(stdscr, str(data))
        #stdscr.refresh()
        #stdscr.getch()
    dic = {}
    dic["flair"] = "tsk"
    dic["text"] = " "
    dic["time"] = int(time())
    data.insert(y+y2, dic)
    stdscr.clear()
    printData(stdscr, data)
    stdscr.refresh()
    stdscr.move(y, scrollx)
    return data


def flipTask(stdscr, data, pos):
    taskFlair = data[pos]["flair"]
    # wr(stdscr, str(type(taskFlair)) + ": " + taskFlair, stdscr.getmaxyx()[0]-1, "force")
    # stdscr.refresh()
    # stdscr.getch()
    taskorder = ["tsk", "suc", "err", "gen"]
    if not taskFlair in taskorder:
        newTaskFlair = "tsk"
    else:
        newTaskFlair = taskorder[(taskorder.index(taskFlair) + 1) % len(taskorder)]
#    if taskFlair == "suc":
#        taskFlair = "err"
#    elif taskFlair == "err":
#        taskFlair = "gen"
#    elif taskFlair == "gen":
#        taskFlair = "tsk"
#    elif taskFlair == "tsk":
#        taskFlair = "suc"
#    else:
#        taskFlair = "tsk"
    # wr(stdscr, str(type(taskFlair)) + ": " + taskFlair, stdscr.getmaxyx()[0]-1, "force")
    # stdscr.refresh()
    # stdscr.getch()
    data[pos]["flair"] = newTaskFlair
    return data


def moveLine(stdscr, data, pos, up=False):
    line = data[pos]
    if up:
        line2 = data[pos-1]
        data[pos], data[pos-1] = line2, line
    else:
        line2 = data[pos+1]
        data[pos], data[pos+1] = line2, line
    return data


def curadd():
    if xwinscroll == 0:
        var = 4
    else:
        var = 0

    return var


def getAllNames(fulldata):
    data = []
    for i in fulldata:
        data.append(i)
    return data

# This function got replaced from within the list to when selecting a list
#
# def rename(stdscr, data):
#     alert(stdscr, "What do you want to rename the list to?")
#     stdscr.refresh()
#     sleep(1)
#     alert(stdscr, "Rename: ")
#     c.echo()
#     stdscr.refresh()
#     newname = input()
#     c.noecho()
#     # TODO: Sørg for at getAllNames under har tilgjengelig riktig variabel
#     if len(newname) > 0 and newname not in getAllNames(fulldata):
#         name = newname
#     else:
#         alert(stdscr, "Invalid name")
#         stdscr.refresh()
#         stdscr.getch()
#         rename(stdscr, data)


def editMode(stdscr, data, pos):
    global ywinscroll
    global xwinscroll

    text = data[pos]
    y = stdscr.getyx()[0]
    x = editx
    #cursorx = stdscr.getyx()[1] - 4

    printData(stdscr, data, pos)

    text = data[pos]["text"]
    #fla = data[pos]["flair"]
    #stdscr.move(stdscr.getyx()[0], 4+len(text))
    viewtext =  text[xwinscroll:stdscr.getmaxyx()[1]+xwinscroll-1]
    wr(stdscr, viewtext, y, "prompt")

#    totaltext = text

    #c.echo()
    #c.cbreak()
    alert(stdscr, "Escape: cancel      Enter: save changes")

    newx = 0
    cursorx = newx

    stdscr.move(y, x)

    writeborder = [3, stdscr.getmaxyx()[1]-3]

    cont = True
    # j = 0
    while cont:
        stdscr.refresh()
        inp = stdscr.getch()
        inp = cleanInp(inp)
        y, x = stdscr.getyx()

        #cursorx = newx + xwinscroll

        removeLast = False

        if inp in Keybinds.enter:
            data[pos]["time"] = int(time())
            data[pos]["text"] = text
            cont = False
            break
        elif inp in Keybinds.escape: #escape
            cont = False
            break
        elif inp in [22]: #ctrl + v
            # ingen enkel måte å grabbe fra clipboard på
            pass
        elif inp in [410]: #win+f
            pass
        elif inp in Keybinds.backspace:
            if cursorx > 0:
                text = text[:cursorx-1] + text[cursorx:]
                cursorx -= 1
                text = text + " "
                removeLast = True
        elif inp in Keybinds.delete: #delete
            if cursorx < len(text):
                text = text[:cursorx] + text[cursorx+1:]
                text = text + " "
                removeLast = True
        elif inp == c.KEY_UP:
            pass
        elif inp == c.KEY_DOWN:
            pass
        elif inp == c.KEY_LEFT:
            cursorx -= 1
        elif inp == c.KEY_RIGHT:
            cursorx += 1
        elif inp in shiftleft or inp in Keybinds.ctrlleft:
            if not " " in text[::-1][len(text)-cursorx:]:
                cursorx = 0
            else:
                if not cursorx == 0:
                    distance = text[::-1][len(text)-cursorx:].index(" ") + 1
                    if cursorx <= 0 + distance:
                        cursorx = 0
                    else:
                        cursorx -= distance
 #           alert(stdscr, "c: " + str(cursorx))
        elif inp in shiftright or inp in Keybinds.ctrlright:
            if not cursorx >= len(text) and text[cursorx] == " ":
                isOnSpace = 1
            else:
                isOnSpace = 0
            if not cursorx == len(text):
                if not " " in text[cursorx + isOnSpace:]:
                    cursorx = len(text)
                else:
                    distance = text[cursorx + isOnSpace:].index(" ") + isOnSpace
                    if cursorx >= len(text) - distance:
                        cursorx = len(text)
                    else:
                        cursorx += distance
            # alert(stdscr, "c: " + str(cursorx) + "  d:" + str(distance))
            # stdscr.refresh()
            # stdscr.getch()
        elif inp in [263]: # ctrl+backspace
            if not " " in text[::-1][len(text)-cursorx:]:
                text = text[cursorx:]
                cursorx = 0
            else:
                if not cursorx == 0:
                    distance = text[::-1][len(text)-cursorx:].index(" ") + 1
                    if cursorx <= 0 + distance:
                        text = text[cursorx:]
                        cursorx = 0
                    else:
                        text = text[:cursorx - distance] + text[cursorx:]
                        cursorx -= distance
 #           alert(stdscr, "c: " + str(cursorx))
        elif inp in [520]: # ctrl+delete
            if not cursorx >= len(text) and text[cursorx] == " ":
                isOnSpace = 1
            else:
                isOnSpace = 0
            if not cursorx == len(text):
                if not " " in text[cursorx + isOnSpace:]:
                    text = text[:cursorx]
                    cursorx = len(text)
                else:
                    distance = text[cursorx + isOnSpace:].index(" ") + isOnSpace
                    if cursorx >= len(text) - distance:
                        text = text[:cursorx]
                        cursorx = len(text)
                    else:
                        text = text[:cursorx] + text[cursorx + distance:]
                        # cursorx += distance
            # alert(stdscr, "c: " + str(cursorx) + "  d:" + str(distance))
            # stdscr.refresh()
            # stdscr.getch()
        elif not len(text) >= 255:
            if not inp == False:
                letter = chr(inp)
                text = text[:cursorx] + letter + text[cursorx:]
                cursorx += 1
        else:
            alert(stdscr, "Unexpected error while trying to edit line")
            # alert(stdscr, "Error: The current line is full.")

        # j += 1
# Fikse cursor pos
        if cursorx >= len(text)+1:
            cursorx = 0
        elif cursorx < 0:
            cursorx = len(text)

        while (cursorx + curadd() - xwinscroll) > writeborder[1]:
            xwinscroll += 8
        while (cursorx + curadd()) < writeborder[0]:
            xwinscroll -= 8

        newx = cursorx + curadd() - xwinscroll

#        timesFillScreen = (cursorx + curadd()) // writeborder[1]
#        amtEightBlocks = stdscr.getmaxyx()[1] // 8
#        times = timesFillScreen * amtEightBlocks
#        xwinscroll = 8 * times


        if newx >= writeborder[1] and xwinscroll <= 247:
            xwinscroll += 8
            #newx -= 8
        elif newx <= writeborder[0] and xwinscroll >= 8:
            xwinscroll -= 8
            #newx += 8

        newx = curadd() + cursorx - xwinscroll

        #wr(stdscr, "cursor: " + str(cursorx) + " ", stdscr.getmaxyx()[0]-1, "force")
        # stdscr.refresh()
        # stdscr.getch()

        #stdscr.move(y, 0)

        viewtext = text[xwinscroll:stdscr.getmaxyx()[1]+xwinscroll-1]
        if len(viewtext) < 1:
            viewtext = viewtext + " "
        while len(viewtext) + curadd() < stdscr.getmaxyx()[1]:
            viewtext += " "
        if xwinscroll == 0:
            wr(stdscr, viewtext, y, "prompt")
        else:
            wr(stdscr, viewtext, y)

        if removeLast:
            text = text[:-1]

        #winrefresh(stdscr, data, "none", y)

        stdscr.move(y, newx)

    xwinscroll = 0
    data[pos]["time"] = int(time())
    return data


def rePrintListNames(stdscr, listofnames):
    stdscr.clear()
    try:
        for i, n in enumerate(listofnames):
            if i == stdscr.getmaxyx()[0]:
                break
            n = "[" + str(i+1) + "] " + n
            n = n[:stdscr.getmaxyx()[1]-1]
            wr(stdscr, n, i)
        return listofnames
    except:
        oops = "Error: storage has been fucked"
        alert(stdscr, oops)
        stdscr.getch()
        print(oops)
        exit()


def getname(stdscr, storage, fulldata):
    # fulldata = readData(stdscr, storage)

    listnames = getAllNames(fulldata)
    cont = True
    cursor = 0
    x = 1
    while cont:
        alert(stdscr, "Choose list" + (255 * " "))
        rePrintListNames(stdscr, listnames)

        stdscr.move(cursor, x)

        key = stdscr.getch()
        if key in Keybinds.enter or key == 32:
            try:
                name = listnames[cursor]
                # debu(stdscr, str(listnames[0]))
                cont = False
            except:
                alert(stdscr, "No list at cursor")
                stdscr.refresh()
        elif cursor > 0 and key == c.KEY_UP:
            cursor -= 1
        elif cursor < len(listnames) and key == c.KEY_DOWN:
            cursor += 1
        elif key in [97, 65, 43]: #a, +
            if len(listnames) < 20:
                listnames.insert(cursor, "")
                stdscr.clear()
                rePrintListNames(stdscr, listnames)
                alert(stdscr, "Name the new list" + (255 * " "))
                stdscr.move(cursor, x+3)
                c.echo()
                stdscr.refresh()
                #inp = input()
                inp = stdscr.getstr(cursor, 4, stdscr.getmaxyx()[1]-5).decode("utf-8")
                c.noecho()
                listnames.pop(cursor)
                if len(inp) > 0 and not inp in listnames:
                    listnames.insert(cursor, inp)
                    # Legge til default content for list skjer i main
                stdscr.move(cursor, x)
                rePrintListNames(stdscr, listnames)
            else:
                alert(stdscr, "Reached maximum number of lists" + (255 * " "))
        elif key in [113, 81, 120, 88, 27, 24]: #q, x og Esc, ctrl+x
            # Quits without saving
            cont = False
            exit()
        elif key in [114, 82]: #r
            tmp = listnames[cursor]
            listnames[cursor] = ""
            rePrintListNames(stdscr, listnames)

            alert(stdscr, "Rename the list" + (255 * " "))

            stdscr.move(cursor, x+3)
            c.echo()
            stdscr.refresh()
            #inp = input()
            inp = stdscr.getstr(cursor, 4, stdscr.getmaxyx()[1]-5).decode("utf-8")
            c.noecho()
            if len(inp) > 1 and not inp in listnames:
                listnames[cursor] = inp
                stdscr.clear()
                rePrintListNames(stdscr, listnames)
            else:
                listnames[cursor] = tmp
            stdscr.move(cursor, x)
            stdscr.refresh()

        elif len(listnames) > 0 and (key in Keybinds.backspace or key in Keybinds.delete): #backspace, delete
            listnames, delname = deleteListName(stdscr, listnames, cursor)
            fulldata.pop(delname)
            writeData(stdscr, storage, fulldata)
            rePrintListNames(stdscr, listnames)
            stdscr.move(cursor, x)
            stdscr.refresh()
        else:
            pass

        # alert(stdscr, str(name))
        # stdscr.refresh()
        # stdscr.getch()
        # alert(stdscr, str(lsitnames))
        # stdscr.refresh()
        # stdscr.getch()

    return name, listnames


def debu(stdscr, text):
    stdscr.clear()
    alert(stdscr, text)
    stdscr.refresh()
    stdscr.getch()
    return True


def updateFulldata(stdscr, fulldata, currentList, listnames=False):
    if not listnames:
        listnames = getAllNames(fulldata)
    else:
        #for i in fulldata:
            # check if there's a one to one correspondence

        if not currentList in fulldata:
            fulldata[currentList] = newfilecontent(True)["general"]
    return fulldata


def run(stdscr, storage):
    global xwinscroll
    global ywinscroll
    fulldata = readData(stdscr, storage)

    currentList, listnames = getname(stdscr, storage, fulldata)
    fulldata = updateFulldata(stdscr, fulldata, currentList, listnames)
    writeData(stdscr, storage, fulldata, currentList)
    data = fulldata[currentList]
    # debu(stdscr, str(fulldata))
    # debu(stdscr, str(currentList))
    # fulldata = addNewList(data)
    # Match up data to titles in fulldata, and add standard content


    # Legg currentList inn som alternativer i full data.
    #for i, v in enumerate(currentList):
    #    if not v in data:
    #        v = {"flair": "gen", "text": "New List", "time": int(time())}
    #        data.insert(i, v)
    #print("her")

    #print(data)
    #while True:
    stdscr.clear()

    printData(stdscr, data)
    stdscr.move(0, scrollx)
    #stdscr.getch()
    #stdscr.refresh()
    #resetView(stdscr, data)
    stdscr.refresh()

    j = 0
    cont = True
    while cont:
        key = stdscr.getch()
        key = cleanInp(key)
        y = stdscr.getyx()[0]

        if key == 32 and xwinscroll <= 0: #space
            forts = True
            while forts:
                data = flipTask(stdscr, data, y+ywinscroll)
                #print(data)
                #stdscr.getch()
                #wr(stdscr, data[y+ywinscroll][1:], y, data[y+ywinscroll]["flair"])
                wr(stdscr, data[y+ywinscroll]["text"], y, data[y+ywinscroll]["flair"])
                stdscr.move(y, scrollx)
                stdscr.refresh()
                k = stdscr.getch()
                k = cleanInp(k)

                if not k == 32:
                    forts = False
                    key = k
            data = sortData(stdscr, data)
            resetView(stdscr, data, y)
        if key == c.KEY_UP:
            scrollup(stdscr, data, y)
        elif key == c.KEY_DOWN:
            scrolldown(stdscr, data, y)
        elif key == c.KEY_RIGHT:
            winrefresh(stdscr, data, "right")
            stdscr.move(y, scrollx)
        elif key == c.KEY_LEFT:
            winrefresh(stdscr, data, "left")
            stdscr.move(y, scrollx)
        elif key in shiftleft:
            while xwinscroll > 0:
                winrefresh(stdscr, data, "left")
            stdscr.move(y, scrollx)
        elif key in shiftright:
            while xwinscroll < 247:
                winrefresh(stdscr, data, "right")
            stdscr.move(y, scrollx)

        elif key in shiftup: #shift+up
            if stdscr.getyx()[0] > 0:
                data = sortData(stdscr, moveLine(stdscr, data, y+ywinscroll, True))
                #stdscr.move(y-1, scrollx)
                resetView(stdscr, data, y-1)
            else:
                if ywinscroll < 0:
                    scrollup(stdscr, data, y)
                    data = sortData(stdscr, moveLine(stdscr, data, y+ywinscroll, True))
                    resetView(stdscr, data, y-1)

        elif key in shiftdown: #shift+down
            if stdscr.getyx()[0] <= stdscr.getmaxyx()[0]-1 and stdscr.getyx()[0] <= len(data)-ywinscroll-2:
                data = sortData(stdscr, moveLine(stdscr, data, y+ywinscroll))
                #stdscr.move(y+1, scrollx)
                resetView(stdscr, data, y+1)
            else:
                if stdscr.getyx()[0] >= stdscr.getmaxyx()[0]-2 and stdscr.getyx()[0] <= len(data)-ywinscroll-2:
                    scrolldown(stdscr, data, y)
                    data = sortData(stdscr, moveLine(stdscr, data, y+ywinscroll))
                    resetView(stdscr, data, y)

        elif key in [43, 97, 65]: #+, a
            #stdscr.move(y, scrollx)
            data = sortData(stdscr, makeNew(stdscr, data, y, ywinscroll))
            data = editMode(stdscr, data, y+ywinscroll)
            resetView(stdscr, data, y)
            #wr(stdscr, "Enter", stdscr.getmaxyx()[0]-1)
            #stdscr.move(y, scrollx)
        elif xwinscroll <= 0 and (key in [100, 68] or key in Keybinds.backspace or key in Keybinds.delete): #backspace, d, delete
            data = youSurePrompt(stdscr, storage, data, y+ywinscroll)
        elif key in [114, 82]: #r
            xwinscroll = 0
            ywinscroll = 0
            resetView(stdscr, data)
        elif key in [104, 72]: #h
            helpfunc(stdscr, storage, data)
        # elif key in [115, 83]: #s
        #     resetView(stdscr, data)
        #     currentList, listnames = getname(stdscr, fulldata)
        #     data = readData(stdscr, storage)
        #     resetView(stdscr, data)
        #     j = 0

        elif key in [110, 78]: #n
            #rename(stdscr, data)
            pass
            # Nothing here
        elif xwinscroll == 0 and (key in Keybinds.enter or key in [101, 69]): #enter, e
            #wr(stdscr, "Space", stdscr.getmaxyx()[0]-1, "force")
            data = editMode(stdscr, data, y+ywinscroll)
            #stdscr.move(y, scrollx)
            resetView(stdscr, data, y)
        elif key in [113, 81, 120, 88, 27, 24]: #q, x og Esc, ctrl+x
            resetView(stdscr, data)
            data = sortData(stdscr, data)
            writeData(stdscr, storage, fulldata, currentList, data)
            cont = False
        else:
            #alert(stdscr, str(type(key)) + ":" + str(key))
            pass

        j += 1
        #alert(stdscr, "Scroll:                      " + str(xwinscroll))

        stdscr.refresh()


def main(stdscr):
    # c blir automatisk passet til main fra wrapper funksjon.
    todo = Todo()
    app = App(stdscr, todo)
    app.set_shorter_esc_delay_in_os()

    c.init_pair(FlairSymbols.color[Flairs.prt], c.COLOR_YELLOW, c.COLOR_BLACK) # Preset farger
    c.init_pair(FlairSymbols.color[Flairs.tsk], c.COLOR_BLUE, c.COLOR_BLACK)
    c.init_pair(FlairSymbols.color[Flairs.suc], c.COLOR_GREEN, c.COLOR_BLACK)
    c.init_pair(FlairSymbols.color[Flairs.err], c.COLOR_RED, c.COLOR_BLACK)
    c.init_pair(FlairSymbols.color[Flairs.gen], c.COLOR_BLACK, c.COLOR_WHITE)

    stdscr.clear()
    c.curs_set(2)
    c.noecho()

    while True:
        app.run()


if __name__ == "__main__":
    c.wrapper(main) # Curses wrapper, calls main.
