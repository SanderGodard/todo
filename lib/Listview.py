class Listview:
    def __init__(self, app):
        self.stdscr = app.stdscr

    def printList(self, entrylist):
        for i, line in enumerate(entrylist):
            leftEntry = f"{line[1]} {line[0]}"
            rightEntry = f"{line[2]}"
            totWidth = self.stdscr.getmaxyx()[1]
            if len(leftEntry) + len(rightEntry) <= totWidth:
                leftEntry = leftEntry[totWidth - len(rightEntry) - 5] + "...  "
            else:
                leftEntry = leftEntry + (" " * (totWidth - len(rightEntry) - len(leftEntry)))
            entry = leftEntry + rightEntry
            
            if i == 0:
                self.wr(line, i, Flairs.inf)
            else:
                self.wr(line, i)
