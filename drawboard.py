# -*- coding: utf-8 -*-
import curses
import time

wait = lambda: time.sleep(1)

STAR = ord('*')

def drawboard(screen):
    board = []
    maxY, maxX = screen.getmaxyx()
    for i in range(maxX):
        # при записи символа в правый нижний угол вылезает исключение, которое можно игнорить
        try:
            board.extend([(0,i), (maxY-1, i)])
            screen.addch(0,   i, STAR)
            screen.addch(maxY-1, i, STAR)
        except curses.error:
            pass
    for i in range(maxY):
        try:
            board.extend([(i, 0), (i, maxX-1)])
            screen.addch(i, maxX-1, STAR)
            screen.addch(i, 0, STAR)
        except curses.error:
            pass
    return board

#    try:
#        screen.addch(maxY-1, maxX-1, ord('/'))
#    except curses.error:
#        pass
#    screen.move(0,0)
##    for j in range(maxY-1):
##        screen.addch(j, 0,    ord('|'))
##        screen.addch(j, maxX-1, ord('|'))
##    except Exception:
##        pass

def main(screen):
    screen.clear()
    drawboard(screen)
    screen.refresh()
    screen.getch()

if __name__ == '__main__':
    curses.wrapper(main)
