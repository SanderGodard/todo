#!/bin/python3
from os import path, mkdir, environ
import curses as c
from platform import system
from time import sleep, time
import json

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
shiftleft = [393, 391]
shiftright = [402, 400]


if system() == "Windows":
    import getpass
    confFolder = 'C:\\Users\\' + getpass.getuser() + '\\todoList\\'
    storage = confFolder + "storage.json"
elif system() == "Linux" or system() == "Darwin":
    try:
        home = path.expanduser("~") + "/"
    except:
        print(err + "Could not find home folder")
        exit()
    confFolder = home + ".config/todo/"
    storage = confFolder + "storage.json"
else:
    print("can't recognize OS, edit script to fit")
    exit()


newfilecontent = """{
	'general' : [
		{
			'flair' : 'gen',
			'text' : 'General todolist',
			'time' : 1605877878
		},
		{
			'flair' : 'gen',
			'text' : ',
			'time' : 1605877878
		},
		{
			'flair' : 'tsk',
			'text' : 'Gjør eom todo til json',
			'time' : 1605877878
		}
    ]
}"""


def set_shorter_esc_delay_in_os():
    environ.setdefault('ESCDELAY', '25')


def helpfunc(stdscr, data):
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

    esc, q, x        :   Exit program"""

    if stdscr.getmaxyx()[1] <= 56:
        helpstr = helpstr.replace("  ", " ")
    if stdscr.getmaxyx()[0] <= 4:
        helpstr = """Make your terminal
        size larget to read
        all the instructions"""
    stdscr.clear()
    for i, line in enumerate(helpstr.splitlines()):
        if i == 0:
            wr(stdscr, line, i, "inf")
        else:
            wr(stdscr, line, i)

    alert(stdscr, "Press any key to exit this menu")

    stdscr.move(0, 1)
    stdscr.refresh()
    wait = stdscr.getch()
    resetView(stdscr, data)


def alert(stdscr, text):
    stdscr.attron(c.color_pair(5))

    #text = "Escape: cancel      Enter: save changes"
    text = text[xwinscroll:stdscr.getmaxyx()[1]+xwinscroll-1]
    if len(text) < 1:
        text = " "
    wr(stdscr, text, stdscr.getmaxyx()[0]-1, "force")

    stdscr.attroff(c.color_pair(5))

    stdscr.refresh()


def cleanInp(inp):
    dict = {165:229, 133:197, 184:248, 152:216, 166:230, 134:198}
    if inp in dict:
        inp = dict[inp]
    elif inp == 195: #Ã
        inp = False
    return inp


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
    # alert(stdscr, str(xwinscroll))
    # stdscr.getch()
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
                file.write(newfilecontent)
            print("Made file: " + storage)
        except:
            print("Could not create file: " + storage)
            exit()


def readData(stdscr, title=False):
    global name
    #try:
    data = []
    with open(storage, "r") as file:
        #for line in file:
        #    print(line)
        fulldata = json.load(file)

    if title == True:
        for i in fulldata:
            data.append(i)
    elif not title:
        for k, v in fulldata.items():
            for j in v:
                #alert(stdscr, str(j))
                #stdscr.getch()
                data.append(j)
            name = k
            return data
    else:
        for i in fulldata:
            # alert(stdscr, i)
            # stdscr.getch()
            # alert(stdscr, str(fulldata[i]))
            # stdscr.getch()
            if title == i or name == i:
                for j in fulldata[i]:
                    data.append(j)
                return data
            # elif i == fulldata[-1]:
            #     for k, v in fulldata.items():
            #         for j in v:
            #             #alert(stdscr, str(j))
            #             #stdscr.getch()
            #             data.append(j)
            #         name = k
            #         return data

    #alert(stdscr, str(data))
    #stdscr.getch()
    return data
    #except:
    #    print("There was a problem reading the data from the storage file in: " + storage + "\n Please ensure the file and folder exists and permissions are correct")
    #    exit()


def printData(stdscr, data=False, focus=False):
    global ywinscroll
    global xwinscroll
    global name
    h, w = stdscr.getmaxyx()
    if len(name) < 0:
        name = False
    if not data:
        data = readData(stdscr, name)
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


def writeData(stdscr, data):
    global name
    #return True
    newdata = {}
    #try:
    names = getAllNames(stdscr)
    for i in names:
        #alert(stdscr, str(i))
        #stdscr.getch()
        if i == name:
            newdata[name] = data
        else:
            newdata[i] = readData(stdscr, i)

    #dat = {}
    #dat[0] = data
    with open(storage, "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    return True
    # except:
    #     #return False
    #     print("Something got fucked while trying to write to storage")
    #     exit()


def sortData(stdscr, data):
    return data


def resetView(stdscr, data, y=0):
    #global ywinscroll
    data = sortData(stdscr, data)
    writeData(stdscr, data)
    stdscr.clear()
    printData(stdscr)
    # stdscr.refresh()
    # stdscr.getch()

    stdscr.move(y, scrollx)
    stdscr.refresh()


def youSurePrompt(stdscr, data, y):
    cont = True

    text = data[y-ywinscroll]["text"][xwinscroll:stdscr.getmaxyx()[1]+xwinscroll-1]
    wr(stdscr, text, y, "prompt")

    alert(stdscr, "Do you want to delete this task? (Y/n) ")

    while cont:
        accept = stdscr.getch()
        accept = cleanInp(accept)
        if accept in enter or accept in [121, 89] or accept in backspace or accept in delete: #enter, y, backspace
            data.pop(y-ywinscroll)
            cont = False
        elif accept in [110, 780, 27, 990, 670, 81, 113]: #n, esc, c, q
            cont = False

    resetView(stdscr, data, y-ywinscroll)
    return data


def deleteList(stdscr, data, y):
    cont = True

    text = data[y]
    wr(stdscr, text, y, "prompt")

    alert(stdscr, "Do you want to delete this task? (Y/n) ")

    while cont:
        accept = stdscr.getch()
        accept = cleanInp(accept)
        if accept in enter or accept in [121, 89] or accept in backspace or accept in delete: #enter, y, backspace
            data.pop(y)
            cont = False
        elif accept in [110, 780, 27, 990, 670, 81, 113]: #n, esc, c, q
            cont = False

    #TODO gjøre så faktisk fjerner
    data = rewritenames(stdscr, data)
    return data


def makeNew(stdscr, data, y=0, y2=0):
    data[y+y2]["flair"] = "tsk"
    data[y+y2]["text"] = " "
    data[y+y2]["time"] = int(time())
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
    if taskFlair == "suc":
        taskFlair = "err"
    elif taskFlair == "err":
        taskFlair = "gen"
    elif taskFlair == "gen":
        taskFlair = "tsk"
    elif taskFlair == "tsk":
        taskFlair = "suc"
    else:
        taskFlair = "tsk"
    # wr(stdscr, str(type(taskFlair)) + ": " + taskFlair, stdscr.getmaxyx()[0]-1, "force")
    # stdscr.refresh()
    # stdscr.getch()
    data[pos]["flair"] = taskFlair
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


def getAllNames(stdscr):
    global storage
    a = readData(stdscr, True)
    #alert(stdscr, str(a))
    #stdscr.getch()
    return a


def rename(stdscr, data):
    global name
    alert(stdscr, "What do you want to rename the list to?")
    stdscr.refresh()
    sleep(1)
    alert(stdscr, "Rename: ")
    c.echo()
    stdscr.refresh()
    newname = input()
    c.noecho()
    if len(newname) > 0 and newname not in getAllNames(stdscr):
        name = newname
    else:
        alert(stdscr, "Invalid name")
        stdscr.refresh()
        stdscr.getch()
        rename(stdscr, data)


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

        if inp in enter:
            data[pos]["time"] = int(time())
            data[pos]["text"] = text
            cont = False
            break
        elif inp in [27]: #escape
            cont = False
            break
        elif inp in [22]: #ctrl + v
            pass
        elif inp in [410]: #win+f
            pass
        elif inp in backspace:
            if cursorx > 0:
                text = text[:cursorx-1] + text[cursorx:]
                cursorx -= 1
                text = text + " "
                removeLast = True
        elif inp in delete: #delete
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
        elif inp in shiftleft:
            if cursorx <= 0 + 5:
                cursorx = 0
            else:
                cursorx -= 5
        elif inp in shiftright:
            if cursorx >= len(text) - 5:
                cursorx = len(text)
            else:
                cursorx += 5
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


def rewritenames(stdscr, data):
    stdscr.clear()
    try:
        for i, n in enumerate(data):
            if i == stdscr.getmaxyx()[0]:
                break
            n = "[" + str(i+1) + "] " + n
            n = n[:stdscr.getmaxyx()[1]-1]
            wr(stdscr, n, i)
        return data
    except:
        oops = "Error: storage has been fucked"
        alert(stdscr, oops)
        stdscr.getch()
        print(oops)
        exit()


def getname(stdscr):
    global name
    data = getAllNames(stdscr)
    cont = True
    cursor = 0
    x = 1
    while cont:
        alert(stdscr, "Choose list" + (255 * " "))
        rewritenames(stdscr, data)

        stdscr.move(cursor, x)

        key = stdscr.getch()
        if key in enter or key == 32:
            name = data[cursor]
            cont = False
        elif cursor > 0 and key == c.KEY_UP:
            cursor -= 1
        elif cursor < len(data) and key == c.KEY_DOWN:
            cursor += 1
        elif len(data) < 10 and key in [97, 65, 43]: #a, +
            alert(stdscr, "Name the new list" + (255 * " "))
            data.insert(cursor, "")
            stdscr.clear()
            rewritenames(stdscr, data)
            stdscr.move(cursor, x+3)
            c.echo()
            stdscr.refresh()
            #inp = input()
            inp = stdscr.getstr(cursor, 4, stdscr.getmaxyx()[1]-5).decode("utf-8")
            c.noecho()
            data.pop(cursor)
            if len(inp) > 1 and not inp in data:
                data.insert(cursor, inp)
            stdscr.move(cursor, x)
        elif key in [113, 81, 120, 88, 27]: #q, x og Esc
            cont = False
            exit()
        elif key in [114, 82]: #r
            tmp = data[cursor]
            data[cursor] = ""
            rewritenames(stdscr, data)

            alert(stdscr, "Rename the list" + (255 * " "))

            stdscr.move(cursor, x+3)
            c.echo()
            stdscr.refresh()
            #inp = input()
            inp = stdscr.getstr(cursor, 4, stdscr.getmaxyx()[1]-5).decode("utf-8")
            c.noecho()
            if len(inp) > 1 and not inp in data:
                data[cursor] = inp
                stdscr.clear()
                rewritenames(stdscr, data)
            stdscr.move(cursor, x)
            stdscr.refresh()
        elif len(data) > 0 and (key in backspace or key in delete): #backspace, delete
            deleteList(stdscr, data, cursor)
            stdscr.move(cursor, x)
            stdscr.refresh()
        else:
            pass

        stdscr.refresh()

    return data


def main(stdscr):
    global ywinscroll
    global xwinscroll
    global name
    c.init_pair(1, c.COLOR_YELLOW, c.COLOR_BLACK)
    c.init_pair(2, c.COLOR_BLUE, c.COLOR_BLACK)
    c.init_pair(3, c.COLOR_GREEN, c.COLOR_BLACK)
    c.init_pair(4, c.COLOR_RED, c.COLOR_BLACK)
    c.init_pair(5, c.COLOR_BLACK, c.COLOR_WHITE)

    stdscr.clear()
    c.curs_set(2)
    c.noecho()
    initCheck(stdscr)

    names = getname(stdscr)
    data = readData(stdscr, name)

    # Legg names inn som alternativer i full data.
    #for i, v in enumerate(names):
    #    if not v in data:
    #        v = {"flair": "gen", "text": "New List", "time": int(time())}
    #        data.insert(i, v)
    #print("her")

    #print(data)
    #while True:
    resetView(stdscr, data)

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
            resetView(stdscr, data, y)
            #wr(stdscr, "Enter", stdscr.getmaxyx()[0]-1)
            #stdscr.move(y, scrollx)
        elif xwinscroll <= 0 and (key in [100, 68] or key in backspace or key in delete): #backspace, d, delete
            data = youSurePrompt(stdscr, data, y+ywinscroll)
        elif key in [114, 82]: #r
            xwinscroll = 0
            ywinscroll = 0
            resetView(stdscr, data)
        elif key in [104, 72]: #h
            helpfunc(stdscr, data)
        elif key in [115, 83]: #s
            resetView(stdscr, data)
            names = getname(stdscr)
            data = readData(stdscr, name)
            resetView(stdscr, data)
            j = 0

        elif key in [110, 78]: #n
            rename(stdscr, data)
            resetView(stdscr, data, y)
        elif xwinscroll == 0 and (key in enter or key in [101, 69]): #enter, e
            #wr(stdscr, "Space", stdscr.getmaxyx()[0]-1, "force")
            data = editMode(stdscr, data, y+ywinscroll)
            #stdscr.move(y, scrollx)
            resetView(stdscr, data, y)
        elif key in [113, 81, 120, 88, 27]: #q, x og Esc
            resetView(stdscr, data)
            cont = False
        else:
            #alert(stdscr, str(type(key)) + ":" + str(key))
            pass

        j += 1
        #alert(stdscr, "Scroll:                      " + str(xwinscroll))

        stdscr.refresh()

set_shorter_esc_delay_in_os()
c.wrapper(main)
