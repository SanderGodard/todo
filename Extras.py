#!/bin/python3


class Keybinds:
    backspace = [8, 127] # utenom ctrl+backspace (263) og c.KEY_BACKSPACE
    delete = [330, 383]
    enter = [10, 13, 15] # ctrl+o (15)
    # enter = [c.KEY_ENTER, 10, 13, 15] # ctrl+o (15)
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
    order = [tsk, suc, err, gen]
    inf = "inf"
    prt = "prt"


class FlairSymbols:
    convert = {
        Flairs.tsk : "[ ]",
        Flairs.suc : "[+]",
        Flairs.err : "[x]",
        Flairs.gen : "[-]",
        Flairs.inf : "[i]",
        Flairs.prt : "[_]"
    }
    color = {
        Flairs.tsk : 2,
        Flairs.suc : 3,
        Flairs.err : 4,
        Flairs.gen : 5,
        Flairs.inf : 2,
        Flairs.prt : 1
    }
