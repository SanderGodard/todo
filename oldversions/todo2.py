#!/bin/python3
from os import path, mkdir
import curses as c
from platform import system

storage = ""
scrollx = 1
editx = 4
ywinscroll = 0
xwinscroll = 0

# Keybinds
backspace = [c.KEY_BACKSPACE, 8, 263]
delete = [330, 383]
enter = [c.KEY_ENTER, 10, 13]
shiftup = [337, 547]
shiftdown = [336, 548]


if system() == "Windows":
    import getpass
    confFolder = 'C:\\Users\\' + getpass.getuser() + '\\todoList\\'
    storage = confFolder + "storage.txt"
elif system() == "Linux" or system() == "Darwin":
    try:
        home = path.expanduser("~") + "/"
    except:
        print(err + "Could not find home folder")
        exit()
    confFolder = home + ".config/todo/"
    storage = confFolder + "storage.txt"
else:
    print("can't recognize OS, edit script to fit")
    exit()


def helpfunc(stdscr, data):
    helpstr = """[i] Keys             :   Actions

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

[i] Press any key to exit this menu"""

    if stdscr.getmaxyx()[1] <= 56:
        helpstr = helpstr.replace("  ", " ")
    if stdscr.getmaxyx()[0] <= 4:
        helpstr = """Make your terminal
        size larget to read
        all the instructions"""
    stdscr.clear()
    for i, line in enumerate(helpstr.splitlines()):
        wr(stdscr, line, i)
    stdscr.move(0, 1)
    stdscr.refresh()
    wait = stdscr.getch()
    resetView(stdscr, data)


def scrollup(stdscr, data, y):
    global ywinscroll
    global xwinscroll
    if stdscr.getyx()[0] <= 0:
        winrefresh(stdscr, data, "up", y)
        shifted = True
    else:
        shifted = False

    if not shifted:
        if stdscr.getyx()[0] > 0:
            stdscr.move(y-1, scrollx)
        else:
            stdscr.move(0, scrollx)
    elif shifted:
        if ywinscroll >= len(data)-1-(stdscr.getmaxyx()[0]-2):
            if len(data)-1 <= (stdscr.getmaxyx()[0]-2):
                stdscr.move(len(data)-1, scrollx)
            else:
                stdscr.move(stdscr.getmaxyx()[0]-2, scrollx)
        else:
            stdscr.move(0, scrollx)
    else:
        stdscr.move(0, scrollx)
    stdscr.refresh()


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
    #printData(stdscr)
    #stdscr.move(stdscr.getyx()[0], scrollx)
    stdscr.refresh()



def wr(stdscr, text, row, flair="", focus=False):
    h, w = stdscr.getmaxyx()
    if not row >= h-1 or flair == "force":
        if flair == "" and w <= len(text):
            text = text[:w-1]
        elif not flair == "" and w <= len(text)+4:
            text = text[:w-5]

        if flair == "prompt":
            prompt = "[_] "
            stdscr.addstr(row, 0, prompt[:1])
            stdscr.attron(c.color_pair(1))
            stdscr.addstr(row, 1, prompt[1:2])
            stdscr.attroff(c.color_pair(1))
            stdscr.addstr(row, 2, prompt[2:])
            if focus:
                stdscr.attron(c.color_pair(5))
                stdscr.addstr(row, len(prompt), text)
                stdscr.attroff(c.color_pair(5))
            else:
                stdscr.addstr(row, len(prompt), text)
        elif flair == "inf":
            inf = "[i] "
            stdscr.addstr(row, 0, inf[:1])
            stdscr.attron(c.color_pair(2))
            stdscr.addstr(row, 1, inf[1:2])
            stdscr.attroff(c.color_pair(2))
            stdscr.addstr(row, 2, inf[2:])
            if focus:
                stdscr.attron(c.color_pair(5))
                stdscr.addstr(row, len(inf), text)
                stdscr.attroff(c.color_pair(5))
            else:
                stdscr.addstr(row, len(inf), text)
        elif flair == "tsk":
            tsk = "[ ] "
            stdscr.addstr(row, 0, tsk[:1])
            stdscr.attron(c.color_pair(2))
            stdscr.addstr(row, 1, tsk[1:2])
            stdscr.attroff(c.color_pair(2))
            stdscr.addstr(row, 2, tsk[2:])
            if focus:
                stdscr.attron(c.color_pair(5))
                stdscr.addstr(row, len(tsk), text)
                stdscr.attroff(c.color_pair(5))
            else:
                stdscr.addstr(row, len(tsk), text)
        elif flair == "suc":
            suc = "[+] "
            stdscr.addstr(row, 0, suc[:1])
            stdscr.attron(c.color_pair(3))
            stdscr.addstr(row, 1, suc[1:2])
            stdscr.attroff(c.color_pair(3))
            stdscr.addstr(row, 2, suc[2:])
            if focus:
                stdscr.attron(c.color_pair(5))
                stdscr.addstr(row, len(suc), text)
                stdscr.attroff(c.color_pair(5))
            else:
                stdscr.addstr(row, len(suc), text)
        elif flair == "err":
            err = "[x] "
            stdscr.addstr(row, 0, err[:1])
            stdscr.attron(c.color_pair(4))
            stdscr.addstr(row, 1, err[1:2])
            stdscr.attroff(c.color_pair(4))
            stdscr.addstr(row, 2, err[2:])
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


def initCheck(stdscr):
    if not path.exists(storage):
        if not path.exists(confFolder):
            try:
                mkdir(confFolder)
                print("Made directory: " + confFolder)
            except:
                print("Could not create directory: " + confFolder)
                exit()
        try:
            with open(storage, "a") as file:
                file.write("Press 'h' for instructions\n-\n#Run todo")
            print("Made file: " + storage)
        except:
            print("Could not create file: " + storage)
            exit()


def readData(stdscr):
    data = []
    with open(storage, "r") as file:
        for line in file.readlines():
            data.append(line.replace("\n", "").strip())

    return data


def printData(stdscr, data=False, focus=False):
    global ywinscroll
    global xwinscroll
    h, w = stdscr.getmaxyx()
    if not data:
        data = readData(stdscr)
    data = data[ywinscroll:ywinscroll+stdscr.getmaxyx()[0]-1]
    for i, text in enumerate(data):
        if xwinscroll <= 0:
            plus = 4
            pre = ""
        else:
            plus = 0
            pre = "<"

        text = pre + text[xwinscroll:stdscr.getmaxyx()[1]+xwinscroll-1]
        if len(text) < 1:
            text = text + " "

        if text[0] == "#":
            if not focus == False and focus == i:
                wr(stdscr, text.replace("#", "", 1), i, "suc", True)
            else:
                wr(stdscr, text.replace("#", "", 1), i, "suc")
        elif text[0] == "/":
            if not focus == False and focus == i:
                wr(stdscr, text.replace("/", "", 1), i, "err", True)
            else:
                wr(stdscr, text.replace("/", "", 1), i, "err")
        elif text[0] == "<":
            if not focus == False and focus == i:
                wr(stdscr, text.replace("<", "", 1), i, True)
            else:
                wr(stdscr, text.replace("<", "", 1), i)
        else:
            if not focus == False and focus == i:
                wr(stdscr, text, i, "tsk", True)
            else:
                wr(stdscr, text, i, "tsk")

def writeData(stdscr, data):
    try:
        with open(storage, "w") as file:
            for line in data:
                file.write(line[:255] + "\n")
        return True
    except:
        return False
        print("Something got fucked while tryng to write to storage")
        exit()


def sortData(stdscr, data):
    newData = []
    done = []
    done2 = []
    for row in data:
        if row[0] == "#":
            done.append(row)
        elif row[0] == "/":
            done2.append(row)
        else:
            newData.append(row)
    for row in done:
        newData.append(row)
    for row in done2:
        newData.append(row)
    return newData


def resetView(stdscr, data, y=0):
    data = sortData(stdscr, data)
    writeData(stdscr, data)
    stdscr.clear()
    printData(stdscr)
    stdscr.move(y, scrollx)
    stdscr.refresh()


def youSurePrompt(stdscr, data, y):
    cont = True
    stdscr.attron(c.color_pair(5))

    instr = "Do you want to delete this task? (Y/n) "
    instr = instr[xwinscroll:stdscr.getmaxyx()[1]+xwinscroll-1]
    if len(instr) < 1:
        instr = " "
    wr(stdscr, instr, stdscr.getmaxyx()[0]-1, "force")

    stdscr.attroff(c.color_pair(5))
    stdscr.refresh()
    while cont:
        accept = stdscr.getch()
        if accept in enter or accept in [121, 89] or accept in backspace: #enter, y, backspace
            data.pop(y)
            cont = False
        elif accept in [110, 780, 270, 990, 670, 81, 113]: #n, esc, c, q
            cont = False
        #else:
            # cont = False
            # resetView(stdscr, data, y)
            # youSurePrompt(stdscr, y, data)
    resetView(stdscr, data, y)


def makeNew(stdscr, data, y=0, y2=0):
    data.insert(y+y2, "-")
    stdscr.clear()
    printData(stdscr, data)
    stdscr.refresh()
    stdscr.move(y, scrollx)
    return data


def flipTask(stdscr, data, pos):
    text = data[pos]
    # wr(stdscr, str(type(text)) + ": " + text, stdscr.getmaxyx()[0]-1, "force")
    # stdscr.refresh()
    # stdscr.getch()
    if text[0] == "#":
        text = text.replace("#", "/", 1)
    elif text[0] == "/":
        text = text.replace("/", "", 1)
    else:
        text = "#" + text
    # wr(stdscr, str(type(text)) + ": " + text, stdscr.getmaxyx()[0]-1, "force")
    # stdscr.refresh()
    # stdscr.getch()
    data[pos] = text
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


def editMode(stdscr, data, pos):
    global ywinscroll
    global xwinscroll

    text = data[pos]
    y = stdscr.getyx()[0]
    x = editx
    #cursorx = stdscr.getyx()[1] - 4

    printData(stdscr, data, pos)

    if text[0] == "#":
        pref = "#"
        text = text.replace("#", "", 1)
    elif text[0] == "/":
        pref = "/"
        text = text.replace("/", "", 1)
    else:
        pref = ""
    #stdscr.move(stdscr.getyx()[0], 4+len(text))
    text =  text[xwinscroll:stdscr.getmaxyx()[1]+xwinscroll-1]
    if len(text) < 1:
        text = text + " "
    wr(stdscr, text, y, "prompt")

    #c.echo()
    #c.cbreak()
    instr = "Escape: cancel      Enter: save changes"
    instr = instr[xwinscroll:stdscr.getmaxyx()[1]+xwinscroll-1]
    if len(instr) < 1:
        instr = " "
    wr(stdscr, instr, stdscr.getmaxyx()[0]-1, "force")
    stdscr.refresh()

    totaltext = text
    stdscr.move(y, x)

    cont = True
    while cont:
        stdscr.refresh()
        inp = stdscr.getch()
        y, x = stdscr.getyx()
        cursorx = x - 4
        removeLast = False
        # Fix så teksten faktisk skrives, og gjør alt smooth. har ikke testets
        # Og så teksten som alt er det vises.
        if inp in enter:
            data[pos] = pref + totaltext
            cont = False
            break
        elif inp in [27]: #escape
            #data[pos] = pref + totaltext
            cont = False
            break
        elif cursorx > 0 and inp in backspace:
            totaltext = totaltext[:cursorx-1] + totaltext[cursorx:]
            if cursorx > 0:
                cursorx = cursorx-1
            totaltext = totaltext + " "
            removeLast = True
        elif inp in delete: #delete
            #cursorx = stdscr.getyc()[1] - 4
            totaltext = totaltext[:cursorx] + totaltext[cursorx+1:]
            totaltext = totaltext + " "
            removeLast = True
        elif inp == c.KEY_LEFT:
            if cursorx > 0:
                cursorx = cursorx-1
            elif cursorx <= 0:
                cursorx = len(text)
        elif inp == c.KEY_RIGHT:
            if cursorx < len(text):
                cursorx = cursorx+1
            elif x >= len(text):
                cursorx = 0
        else:
            letter = chr(inp)
            totaltext = totaltext[:cursorx] + letter + totaltext[cursorx:]
            cursorx = cursorx+1

        tmpy, tmpx = stdscr.getyx()
        stdscr.move(tmpy, 0)

        text = totaltext[xwinscroll:stdscr.getmaxyx()[1]+xwinscroll-1]
        if len(text) < 1:
            text = text + " "
        wr(stdscr, text, tmpy, "prompt")
        #stdscr.move(y, x)
        if removeLast:
            totaltext = totaltext[:-1]

        if cursorx >= stdscr.getmaxyx()[1]-3:
            winrefresh(stdscr, data, "right")
            cursorx = cursorx-8
        elif cursorx >= 3 and xwinscroll > 0:
            winrefresh(stdscr, data, "left")
            cursorx = cursorx+8

        stdscr.move(y, cursorx + 4)


    #wr(stdscr, text, y)

    #stdscr.refresh()
    #wr(stdscr, inp, stdscr.getmaxyx()[0]-1, "force")
    #c.noecho()
    #c.nocbreak()
    #data[pos] = text
    return data


def main(stdscr):
    global ywinscroll
    global xwinscroll
    c.init_pair(1, c.COLOR_YELLOW, c.COLOR_BLACK)
    c.init_pair(2, c.COLOR_BLUE, c.COLOR_BLACK)
    c.init_pair(3, c.COLOR_GREEN, c.COLOR_BLACK)
    c.init_pair(4, c.COLOR_RED, c.COLOR_BLACK)
    c.init_pair(5, c.COLOR_BLACK, c.COLOR_WHITE)

    stdscr.clear()
    c.curs_set(2)
    c.noecho()
    initCheck(stdscr)
    data = readData(stdscr)
    #print(data)
    #while True:
    resetView(stdscr, data)

    stdscr.refresh()



    j = 0
    cont = True
    while cont:
        key = stdscr.getch()
        y = stdscr.getyx()[0]

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

        elif key in shiftup: #shift+up
            data = sortData(stdscr, moveLine(stdscr, data, y+ywinscroll, True))
            #stdscr.move(y-1, scrollx)
            resetView(stdscr, data, y-1)
        elif key in shiftdown: #shift+down
            data = sortData(stdscr, moveLine(stdscr, data, y+ywinscroll))
            #stdscr.move(y+1, scrollx)
            resetView(stdscr, data, y+1)


        elif key in [43, 97, 65]: #+, a
            #stdscr.move(y, scrollx)
            data = sortData(stdscr, makeNew(stdscr, data, y, ywinscroll))
            #wr(stdscr, "Enter", stdscr.getmaxyx()[0]-1)
            #stdscr.move(y, scrollx)
        elif xwinscroll <= 0 and (key in [100, 68] or key in backspace): #backspace, d
            youSurePrompt(stdscr, data, y+ywinscroll)
        elif key in [114, 82]: #r
            resetView(stdscr, data)
        elif key in [104, 72]: #h
            helpfunc(stdscr, data)
        elif key == 32 and xwinscroll <= 0: #space
            #wr(stdscr, "Space", stdscr.getmaxyx()[0]-1, "force")
            data = sortData(stdscr, flipTask(stdscr, data, y+ywinscroll))
            #stdscr.move(y, scrollx)
            resetView(stdscr, data, y)
        elif key in enter or key in [101, 69]: #enter, e
            #wr(stdscr, "Space", stdscr.getmaxyx()[0]-1, "force")
            data = editMode(stdscr, data, y+ywinscroll)
            #stdscr.move(y, scrollx)
            resetView(stdscr, data, y)
        elif key in [113, 81, 120, 88, 27]: #q, x og Esc
            resetView(stdscr, data)
            cont = False
        else:
            #wr(stdscr, str(type(key)) + ":" + str(key), stdscr.getmaxyx()[0]-1)
            pass


        # Om denne skal være en recursive function eller loop, hvis recursive kan jeg passe oppdatert data mellom hver gang.

        j += 1
        #y = stdscr.getyx()[0]
        #wr(stdscr, str(y+ywinscroll) + "    ", stdscr.getmaxyx()[0]-1, "force")
        #stdscr.move(y, scrollx)
        #stdscr.move(y, scrollx)
        stdscr.refresh()


    #window.scroll(-5)
    #c.doupdate()
    #c.refresh()


c.wrapper(main)
