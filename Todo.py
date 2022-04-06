#!/bin/python3
from os import path, mkdir, environ
import curses as c
from platform import system
from time import sleep, time
import json


class Keybinds:
    backspace = [8, 127] # utenom ctrl+backspace (263) og c.KEY_BACKSPACE
    delete = [330, 383]
    enter = [c.KEY_ENTER, 10, 13, 15] # ctrl+o (15)
    escape = [27, 24] # ctrl+x (24)
    shiftup = [337, 547]
    shiftdown = [336, 548]
    shiftleft = [393, 391]
    shiftright = [402, 400]
    ctrlleft = [546, 544]
    ctrlright = [561, 559]
    # CTRL + delete
    # CTRL + backspace
    # add


class Flairs:
    tsk = "tsk"
    suc = "suc"
    err = "err"
    gen = "gen"
    order = [self.tsk, self.suc, self.err, self.gen]
    inf = "inf"
    prompt = "prompt"


class Todo:
    def __init__(self):
        self.entryLists = []


    def createStorage(self):
        if self.storage in locals():
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
            e = EntryList()
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
            eL = EntryList(name=k)
            for eDict in v:
                e = Entry(text=eDict["text"], flair=eDict["flair"], time=eDict["time"])
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
            file.write(str(json.dumps(self.jsonify())))


    def getEntryLists(self):
        return self.entryLists


    def __repr__():
        return f"Todo(entryLists={len(entryLists)}, {storage=})"


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


    def wr(self):
        return


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


    def scrollup(self):
        if self.stdscr.getyx()[0] <= 0:
            winrefresh(self.stdscr, self.getData(), "up", scrolly)
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


    def __repr__(self):
        return f"App({stdscr=})"



def set_shorter_esc_delay_in_os():
    environ.setdefault('ESCDELAY', '25')


def cleanInp(inp):
    dict = {165:229, 133:197, 184:248, 152:216, 166:230, 134:198}
    if inp in dict:
        inp = dict[inp]
    elif inp == 195: #Ã
        inp = False
    return inp



def scrolldown(stdscr, data, y):
    global ywinscroll
    global xwinscroll
    if stdscr.getyx()[0] >= stdscr.getmaxyx()[0]-2 or ywinscroll+stdscr.getyx()[0] >= len(data)-1:
        winrefresh(stdscr, data, "down", y)
        shifted = True
    else:
        shifted = False

    if not shifted:
        if stdscr.getyx()[0] < (stdscr.getmaxyx()[0]-2) or ywinscroll+stdscr.getyx()[0] <= len(data)-1:
            stdscr.move(y+1, scrollx)
        else:
            stdscr.move(0, scrollx)
    elif shifted:
        if ywinscroll <= 0:
            stdscr.move(0, scrollx)
        else:
            stdscr.move(y, scrollx)
    else:
        stdscr.move(0, scrollx)
    stdscr.refresh()


def winrefresh(stdscr, data, direction="none", y=0):
    global ywinscroll
    global xwinscroll
    if direction == "up":
        if ywinscroll <= 0:
            if len(data)-1 <= (stdscr.getmaxyx()[0]-2):
                ywinscroll = 0
            else:
                ywinscroll = len(data)-1-(stdscr.getmaxyx()[0]-2)
        else:
            ywinscroll -= 1

    if direction == "down":
        if ywinscroll >= len(data)-(stdscr.getmaxyx()[0]-2) or ywinscroll+stdscr.getyx()[0] >= len(data)-1:
            ywinscroll = 0
        else:
            ywinscroll += 1

    elif direction == "right" and xwinscroll <= 247:
        xwinscroll += 8
    elif direction == "left" and xwinscroll >= 8:
        xwinscroll -= 8

    stdscr.clear()
    # printData(stdscr, data, False, ywinscroll, xwinscroll)
    printData(stdscr, data, False)
    # alert(stdscr, str(xwinscroll))
    # stdscr.getch()
    #printData(stdscr)
    #stdscr.move(stdscr.getyx()[0], scrollx)
    stdscr.refresh()


def wr(stdscr, text, row, flair="", focus=False):
    h, w = stdscr.getmaxyx()
    if not row >= h-1 or flair == "force":
        if not flair in ["", "force"]:
            text = text[:w-5]
        else:
            text = text[:w-1]

        if flair == "prompt":
            prompt = "[_] "
            stdscr.attron(c.color_pair(1))
            stdscr.addstr(row, 0, prompt)
            stdscr.attroff(c.color_pair(1))
            if focus:
                stdscr.attron(c.color_pair(5))
                stdscr.addstr(row, len(prompt), text)
                stdscr.attroff(c.color_pair(5))
            else:
                stdscr.addstr(row, len(prompt), text)
        elif flair == "inf":
            inf = "[i] "
            stdscr.attron(c.color_pair(2))
            stdscr.addstr(row, 0, inf)
            stdscr.attroff(c.color_pair(2))
            if focus:
                stdscr.attron(c.color_pair(5))
                stdscr.addstr(row, len(inf), text)
                stdscr.attroff(c.color_pair(5))
            else:
                stdscr.addstr(row, len(inf), text)
        elif flair == "tsk":
            tsk = "[ ] "
            stdscr.attron(c.color_pair(2))
            stdscr.addstr(row, 0, tsk)
            stdscr.attroff(c.color_pair(2))
            if focus:
                stdscr.attron(c.color_pair(5))
                stdscr.addstr(row, len(tsk), text)
                stdscr.attroff(c.color_pair(5))
            else:
                stdscr.addstr(row, len(tsk), text)
        elif flair == "suc":
            suc = "[+] "
            stdscr.attron(c.color_pair(3))
            stdscr.addstr(row, 0, suc)
            stdscr.attroff(c.color_pair(3))
            if focus:
                stdscr.attron(c.color_pair(5))
                stdscr.addstr(row, len(suc), text)
                stdscr.attroff(c.color_pair(5))
            else:
                stdscr.addstr(row, len(suc), text)
        elif flair == "err":
            err = "[x] "
            stdscr.attron(c.color_pair(4))
            stdscr.addstr(row, 0, err)
            stdscr.attroff(c.color_pair(4))
            if focus:
                stdscr.attron(c.color_pair(5))
                stdscr.addstr(row, len(err), text)
                stdscr.attroff(c.color_pair(5))
            else:
                stdscr.addstr(row, len(err), text)
        elif flair == "gen":
            err = "[-] "
            stdscr.addstr(row, 0, err)
            if focus:
                stdscr.attron(c.color_pair(5))
                stdscr.addstr(row, len(err), text)
                stdscr.attroff(c.color_pair(5))
            else:
                stdscr.addstr(row, len(err), text)
        else:
            if focus:
                stdscr.attron(c.color_pair(5))
                stdscr.addstr(row, 0, text)
                stdscr.attroff(c.color_pair(5))
            else:
                stdscr.addstr(row, 0, text)


# def initCheck(stdscr, storage, confFolder):
#     if not path.exists(storage):
#         if not path.exists(confFolder):
#             try:
#                 mkdir(confFolder)
#                 print("Made directory: " + confFolder)
#             except:
#                 print("Could not create directory: " + confFolder)
#                 exit()
#         try:
#             # debu(stdscr, str(json.dumps(newfilecontent())))
#             with open(storage, "w") as file:
#                 file.write(str(json.dumps(newfilecontent())))
#             print("Made file: " + storage)
#         except:
#             print("Could not create file: " + storage)
#             exit()


def readData(stdscr, storage):
    with open(storage, "r") as file:
        try:
            fulldata = json.load(file)
            # debu(stdscr, str(fulldata))
        except:
            debu(stdscr, "Try deleting ~/.todo/storage.json, it may be corrupt")
            exit()

    if len(str(fulldata)) == 0:
        fulldata = {"general":[{"flair":"tsk","text":"List cannot be empty :)","time":int(time())}]}
        # data = {"general":[{"flair":"tsk","text":"List cannot be empty :)","time":int(time())}]}
    return fulldata



def printData(stdscr, data, focus=False):
    global ywinscroll
    global xwinscroll
    h, w = stdscr.getmaxyx()
    # if len(name) < 0:
    #     name = False
    data = data[ywinscroll:ywinscroll+stdscr.getmaxyx()[0]-1]
    for i, text in enumerate(data):
        #alert(stdscr, data)
        #stdscr.getch()
        # alert(stdscr, text)
        # stdscr.getch()
        #text = text["text"]
        if xwinscroll <= 0:
            plus = 4
            scrolled = False
        else:
            plus = 0
            scrolled = True
        # debu(stdscr, str(text))
        # debu(stdscr, str(data))
        text = text["text"][xwinscroll:stdscr.getmaxyx()[1]+xwinscroll-1]
        if len(text) < 1:
            text = text + " "

        #alert(stdscr, str(data[i]))
        #stdscr.getch()
        if scrolled or data[i]["flair"] == "pil":
            if not focus == False and focus == i:
                wr(stdscr, text, i, True)
            else:
                wr(stdscr, text, i)
        elif data[i]["flair"] in ["suc", "err", "tsk", "gen"]:
            if not focus == False and focus == i:
                wr(stdscr, text, i, data[i]["flair"], True)
            else:
                wr(stdscr, text, i, data[i]["flair"])
        else:
            if not focus == False and focus == i:
                wr(stdscr, text, i, "tsk", True)
            else:
                wr(stdscr, text, i, "tsk")


def writeData(stdscr, storage, fulldata, currentList=False, data=False):
    if not data or currentList:
        pass
    else:
        #return True
        newdata = {}
        #try:
        # TODO: Sørg for at linjen under har tilgjengelig informasjon
        names = getAllNames(fulldata)
        for i in names:
            #alert(stdscr, str(i))
            #stdscr.getch()
            if i == currentList:
                fulldata[currentList] = data
            # else:
            #     newdata[i] = readData(stdscr, i)

        #dat = {}
        #dat[0] = data

    #Her må noe fikses...
    # debu(stdscr, str(fulldata))
    with open(storage, "w") as file:
        #data = json.dumps(data, indent=4)
        json.dump(fulldata, file, ensure_ascii=False, indent=4)
        # file.write(json.dumps(fulldata, ensure_ascii=False, indent=4))
        # Start med denne linja
    return True
    # except:
    #     #return False
    #     print("Something got fucked while trying to write to storage")
    #     exit()


def sortData(stdscr, data):
    return data


def resetView(stdscr, data, y=0):
    #global ywinscroll

#
#
#		Commentet ut linja over her for å se om det fikser noe.
#
#

    stdscr.clear()
    printData(stdscr, data)
    # stdscr.refresh()
    # stdscr.getch()

    stdscr.move(y, scrollx)
    stdscr.refresh()


def youSurePrompt(stdscr, storage, data, y):
    cont = True

    text = data[y-ywinscroll]["text"][xwinscroll:stdscr.getmaxyx()[1]+xwinscroll-1]
    wr(stdscr, text, y, "prompt")

    alert(stdscr, "Do you want to delete this task? (Y/n) ")

    while cont:
        accept = stdscr.getch()
        accept = cleanInp(accept)
        if accept in Keybinds.enter or accept in [121, 89] or accept in Keybinds.backspace or accept in Keybinds.delete: #enter, y, backspace
            data.pop(y-ywinscroll)
            cont = False
        elif accept in [110, 780, 27, 990, 670, 81, 113]: #n, esc, c, q
            cont = False

    resetView(stdscr, data, y-ywinscroll)
    return data


def deleteListName(stdscr, listofnames, y):
    text = listofnames[y]
    wr(stdscr, text, y, "prompt")
    alert(stdscr, "Do you want to delete this list? (Y/n) ")

    cont = True
    while cont:
        accept = stdscr.getch()
        accept = cleanInp(accept)
        if accept in Keybinds.enter or accept in [121, 89] or accept in Keybinds.backspace or accept in Keybinds.delete: #enter, y, backspace
            delname = listofnames.pop(y)
            cont = False
        elif accept in [110, 780, 27, 990, 670, 81, 113]: #n, esc, c, q
            cont = False

    #TODO gjøre så faktisk fjerner
    return listofnames, delname


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
    global ywinscroll
    global xwinscroll

    todo = Todo()
    app = App(stdscr, todo)

    c.init_pair(1, c.COLOR_YELLOW, c.COLOR_BLACK) # Preset farger
    c.init_pair(2, c.COLOR_BLUE, c.COLOR_BLACK)
    c.init_pair(3, c.COLOR_GREEN, c.COLOR_BLACK)
    c.init_pair(4, c.COLOR_RED, c.COLOR_BLACK)
    c.init_pair(5, c.COLOR_BLACK, c.COLOR_WHITE)

    stdscr.clear()
    c.curs_set(2)
    c.noecho()
    initCheck(stdscr, storage, confFolder)

    while True:
        app.run()
        run(stdscr, storage)



set_shorter_esc_delay_in_os()
c.wrapper(main)
