# -*- coding: utf-8 -*-
import curses
import random
import time


LAND = ord('S')
SEE = ord(' ') 
OVERBOARD = -1


class Screen(object):
    def __init__(self, stdscreen):
        self.scr = stdscreen
        y, x = self.scr.getmaxyx()
        self.matrix = [[ord(' ')]*y for i in range(x)]
        self.scr.clear()
        self.scr.refresh()
        curses.curs_set(0)

    def set(self, ch, x, y):
        self.matrix[x][y] = ch
        try:
            self.scr.addch(y, x, ch)
        except curses.error: # bottom-right catching
            pass

    def get(self, x, y):
        try:
            if x < 0 or y < 0:
                raise IndexError
            return self.matrix[x][y]
        except IndexError:
            return OVERBOARD

    def refresh(self):
        self.scr.refresh()
        



class ReflectingPoint(object):
    def __init__(self, screen, x, y, native_land, reflect_land, ch=ord('O')):
        self.screen = screen
        self.ch = ch
        self.vel = (random.choice([-1, +1]), random.choice([-1, +1]))
        self.pos = [x, y]
        self.native = native_land # LAND or SEE for ex
        self.reflect = reflect_land # list !!

    def move(self):
        # deprecated:       """ reflector -> list of point pairs """
        self.screen.set(self.native, *self.pos)
        
        # если перед точкой нет отражающих частей, то едем дальше
        A  = self.screen.get(self.pos[0] + self.vel[0], self.pos[1] + self.vel[1])
        B0 = self.screen.get(self.pos[0] + self.vel[0], self.pos[1])
        B1 = self.screen.get(self.pos[0],               self.pos[1] + self.vel[1])
        C0 = self.screen.get(self.pos[0] + self.vel[0], self.pos[1] - self.vel[1])
        C1 = self.screen.get(self.pos[0] - self.vel[0], self.pos[1] + self.vel[1])

        # если в мэйн англ есть например игрок, то надо кидать событие куданибудь
        

        main_angle = (A, B0, B1)
        if all(self.native == x or self.ch == x for x in main_angle):
            pass
        # хотябы один либо reflect, либо border, (либо игрок, но это позже)
        else:
            newvels = [( self.vel[0], -self.vel[1]),
                       (-self.vel[0],  self.vel[1]),
                       (-self.vel[0], -self.vel[1])]
            if B0 in self.reflect:
                if B1 in self.reflect or C1 in self.reflect:
                    self.vel = newvels[2]
                else:
                    self.vel = newvels[1]
            elif B1 in self.reflect:
                if B0 in self.reflect or C0 in self.reflect:
                    self.vel = newvels[2]
                else:
                    self.vel = newvels[0]
            else: # only A in main angle
                if C0 in self.reflect:
                    del newvels[0]
                if C1 in self.reflect:
                    del newvels[1]
                self.vel = random.choice(newvels)

        for i in 0, 1:
            self.pos[i] += self.vel[i]
        
        self.screen.set(self.ch, *self.pos)

                
                
def reflect_test(stdscr):
    screen = Screen(stdscr)
    point0 = ReflectingPoint(screen, 13, 15, SEE, (LAND, OVERBOARD))
    point1 = ReflectingPoint(screen, 4, 7, SEE, (LAND, OVERBOARD))
    point2 = ReflectingPoint(screen, 5, 7, SEE, (LAND, OVERBOARD))
    point3 = ReflectingPoint(screen, 4, 13, SEE, (LAND, OVERBOARD))
    point4 = ReflectingPoint(screen, 16, 20, SEE, (LAND, OVERBOARD))
    while True:
        time.sleep(0.1)
        point0.move()
        point1.move()
        point2.move()
        point3.move()
        point4.move()
        screen.refresh()

if __name__ == '__main__':
    curses.wrapper(reflect_test)
