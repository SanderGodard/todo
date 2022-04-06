#!/bin/python3
import curses as c

scrollx = 0

def resetView(stdscr):
    stdscr.clear()
    stdscr.move(0, scrollx)
    stdscr.refresh()

def main(stdscr):
    stdscr.clear()
    c.curs_set(0) # invisible cursor
    c.echo()
    c.init_pair(1, c.COLOR_GREEN, c.COLOR_BLACK)
    c.init_pair(2, c.COLOR_BLACK, c.COLOR_WHITE)


    cont = True
    while cont:
        stdscr.move(0, 0)
        key = stdscr.getch()
        #stdscr.addstr(0, 1, "           ")
        #stdscr.clear()
        y = stdscr.getyx()[0]

        if key == 113: #q
            cont = False
        else:
            #stdscr.attron(c.color_pair(2))
            #stdscr.attron(c.color_pair(1))
            stdscr.addstr(stdscr.getmaxyx()[0]-1, 0, "Keycode: ")
            #tdscr.attroff(c.color_pair(1))
            stdscr.addstr(stdscr.getmaxyx()[0]-1, 9, str(key) + "           ")
            #stdscr.attroff(c.color_pair(2))
        stdscr.refresh()


c.wrapper(main)
