import curses
import time

class Screen(object):
    def __init__(self, screen):
        self.screen = screen

def InitPoint(screen):
    class Point(object):
        def __init__(self, y, x):
            self.x = x
            self.y = y

        def pos(self):
            return self.y, self.x

        def addch(self, ch):
            screen.addch(self.y, self.x, ch)

        def clr(self):
            screen.addch(self.y, self.x, ord(' '))

        def up(self):    self.y -= 1
        def left(self):  self.x -= 1
        def right(self): self.x += 1
        def down(self):  self.y += 1


    return Point
            

def keyloop(stdscr):
    Point = InitPoint(stdscr)
    stdscr.clear()
    stdscr.refresh()
    stdscr.move(0,0)
    bnd = Point(*stdscr.getmaxyx())
    center = Point(bnd.y//2, bnd.x//2)
#    current = Point(
    xpos, ypos = scrX//2, scrY//2
    stdscr.nodelay(1)
    yvel, xvel = 0, 0
    while True:
        ypos += yvel
        xpos += xvel
        stdscr.addch(ypos, xpos, ord('0'))
        c = stdscr.getch()
        if 0 < c < 256:
            c = chr(c)
            if c in 'qQ':
                break
        elif c == curses.KEY_UP and ypos>0:         yvel = -1; xvel=0
        elif c == curses.KEY_DOWN and ypos<scrY-1:  yvel = 1 ; xvel=0
        elif c == curses.KEY_LEFT and xpos>0:       xvel = -1; yvel=0
        elif c == curses.KEY_RIGHT and xpos<scrX-1: xvel = 1 ; yvel=0
        else:
            pass
        time.sleep(0.25)

    

def main(stdscr):
    keyloop(stdscr)             



if __name__ == '__main__':
    curses.wrapper(main)
