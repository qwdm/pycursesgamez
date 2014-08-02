# -*- coding: utf-8 -*-
import curses
import time
import random

from drawboard import drawboard

BOARD = []
BUNNY_EATEN = False

class GameOver(Exception):
    pass

class Snake(object):
    def __init__(self, screen, init_len=7, ch=ord('0'), grow_rate=3):
        self.pieces = []
        self.screen = screen
        self.ch = ch
        self.vel = (0,0)
        self.grow_rate = grow_rate

        maxY, maxX = screen.getmaxyx()
        centY, centX = maxY//2, maxX//2
        for i in range(init_len):
            self.pieces.append((centY, centX-i))
        self.draw()

    def draw(self):
        for p in self.pieces:
            self.screen.addch(p[0], p[1], self.ch)
        self.screen.move(0,0)

    def turn(self, direction):
        directions = {
                'up': (-1, 0),
                'down': (1,0),
                'left': (0, -1),
                'right': (0, 1)
        }
        self.vel = directions[direction]

    def set_bunny(self, bunny):
        self.bunny = bunny

    def move(self):
        bunny_eaten = False
        head = self.pieces[0]
        tail = self.pieces[-1]

        newhead = head[0] + self.vel[0], head[1] + self.vel[1]

        if newhead in self.pieces or newhead in BOARD:
            raise GameOver

        if newhead == self.bunny.coord():
            self.isgrowing += self.grow_rate
            bunny_eaten = True

        if not self.isgrowing:
            self.screen.addch(tail[0], tail[1], ord(' '))
            self.pieces = [newhead] + self.pieces[:-1]
        else:
            self.pieces = [newhead] + self.pieces
            self.isgrowing -= 1

        if bunny_eaten:
            self.bunny.new(self.pieces)

    def start(self):
        self.isgrowing = 0
        self.bunny.new(self.pieces)
        self.draw()
        self.screen.getch()
        self.turn('right')


class Bunny(object):
    def __init__(self, screen):
        self.screen = screen

    def new(self, forbidden):
        maxY, maxX = self.screen.getmaxyx()

        def inside_board_rand(maxSmth):
            return int(random.random() * (maxSmth-2)) + 1

        while True:
            self.x = inside_board_rand(maxX) 
            self.y = inside_board_rand(maxY)
            if (self.y, self.x) in forbidden:
                continue
            else:
                break

        self.screen.addch(self.y, self.x, ord('$'))

    def coord(self):
        return self.y, self.x


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
    try:
        bunny = Bunny(stdscr)
        snake = Snake(stdscr)
        snake.set_bunny(bunny)

        stdscr.nodelay(0)
        stdscr.clear()

        global BOARD
        BOARD = drawboard(stdscr)
#        Point = InitPoint(stdscr)
        stdscr.refresh()
        stdscr.move(0,0)
        snake.start()
        stdscr.nodelay(1)
        while True:
            snake.draw()
            stdscr.move(0,0)
            stdscr.refresh()
            time.sleep(0.1)
            c = stdscr.getch()
            if 0 < c < 256:
                c = chr(c)
                if c in 'qQ':
                    break
            elif c == curses.KEY_UP:        snake.turn('up')
            elif c == curses.KEY_DOWN:      snake.turn('down')
            elif c == curses.KEY_LEFT:      snake.turn('left')
            elif c == curses.KEY_RIGHT:     snake.turn('right')
            else:
                pass
            
            snake.move()
            
    except GameOver:
        main(stdscr)


    

def main(stdscr):
    keyloop(stdscr)             



if __name__ == '__main__':
    curses.wrapper(main)
