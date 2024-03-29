# -*- coding: utf-8 -*-
import curses
import random
import time

import sys
sys.setrecursionlimit(10000)

LAND = ord('S') # земля, нативная область для игрока
SEE = ord(' ')  # море, область для захвата
OVERBOARD = -1  # guard для выхода за границу
PLAYER = ord('*') # голова игрока
TRACK = ord('+')  # шлейф на море
SEEMONSTER = ord('O')


class State(object):
    def __init__(self, state=None):
        self._state = state 

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

STATE = State()


class Screen(object):
    def __init__(self, stdscreen):
        self.scr = stdscreen
        y, x = self.scr.getmaxyx()
        self.matrix = [[ord(' ')]*y for i in range(x)]
        self.scr.clear()
        self.scr.refresh()
        curses.curs_set(0)
        self.maxX = x
        self.maxY = y
        self.scr.nodelay(1)

        self.monsters = []
        

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

    def fill_init(self):
        for i in range(self.maxX):
            for j in range(2):
                self.set(LAND, i, j)
                self.set(LAND, i, self.maxY-1-j)
        for i in range(self.maxY):
            for j in range(3):
                self.set(LAND, j, i)
                self.set(LAND, self.maxX-1-j, i)
        self.scr.refresh()

    def getch(self):
        return self.scr.getch()

    def make_see(self, positions):
        for p in positions:
            self.set(SEE, *p)
        self.refresh()

    def fill_new_land(self):
        def fill_0(x, y): # заполонить символом 'A' все, куда достают монстры
            val = self.matrix[x][y]
            if val == SEE or val == SEEMONSTER:
                if val != SEEMONSTER:
                    self.set('A', x, y)
                fill_0(x, y+1)
                fill_0(x, y-1)
                fill_0(x+1, y)
                fill_0(x-1, y)

        for m in self.monsters:
            fill_0(*m.pos)

        for i in range(self.maxX):
            for j in range(self.maxY):
                if self.matrix[i][j] == SEE:
                    self.set(LAND, i, j)
                elif self.matrix[i][j] == 'A':
                    self.set(SEE, i, j)

        self.refresh()
        




class ReflectingPoint(object):
    def __init__(self, screen, x, y, native_land, reflect_land, ch=ord('O')):
        self.screen = screen
        self.ch = ch
        self.vel = (random.choice([-1, +1]), random.choice([-1, +1]))
        self.pos = [x, y]
        self.native = native_land # LAND or SEE for ex
        self.reflect = reflect_land # list of possible reflectors

    def move(self):
        self.screen.set(self.native, *self.pos)
        
        # если перед точкой нет отражающих частей, то едем дальше
        A  = self.screen.get(self.pos[0] + self.vel[0], self.pos[1] + self.vel[1])
        B0 = self.screen.get(self.pos[0] + self.vel[0], self.pos[1])
        B1 = self.screen.get(self.pos[0],               self.pos[1] + self.vel[1])
        C0 = self.screen.get(self.pos[0] + self.vel[0], self.pos[1] - self.vel[1])
        C1 = self.screen.get(self.pos[0] - self.vel[0], self.pos[1] + self.vel[1])

        # если в мэйн англ есть например игрок, то надо кидать событие куданибудь
        
        main_angle = (A, B0, B1)
        if all(self.native == x or 
               self.ch == x 
               for x in main_angle):
            pass
        # хотябы один либо reflect, либо border, (либо игрок, но это позже)
        elif any(x == TRACK or x == PLAYER for x in main_angle):
            if STATE.state == LAND:
                pass
            else:
                STATE.state = 'loose'
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
    


class Player(object):
    def __init__(self, screen, x, y):
        self.screen = screen
        self.pos = [x, y]
        self.screen.set(PLAYER, x, y)
        self.vel = [0,0]

        self.state = LAND

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, val):
        self._state = val
        STATE.state = val


    def move(self, direction):
        if STATE.state == 'loose':
            self.loose_back()
        init_pos = self.pos[:]
        if self.state == LAND:
            self.screen.set(LAND, *self.pos)
        elif self.state == SEE:
            self.screen.set(TRACK, *self.pos)
        else:
            pass

        if direction == 'left' and self.pos[0] != 0:
            self.pos[0] -= 1
        elif direction == 'right' and self.pos[0] != self.screen.maxX-1:
            self.pos[0] += 1
        elif direction == 'up' and self.pos[1] != 0:
            self.pos[1] -= 1
        elif direction == 'down' and self.pos[1] != self.screen.maxY-1:
            self.pos[1] += 1
        else:
            pass
        
    
        val = self.screen.get(*self.pos)
        if val == SEE and self.state == LAND:
            self.state = SEE
            self.see_start = init_pos # при попадании врага, оказываемся там 
            self.track = [self.pos[:]] 
        elif val == LAND and self.state == SEE:
            self.state = LAND
            self.fill_new_land()
        elif val == SEEMONSTER or val == TRACK:
            self.loose_back()

        if val == SEE and self.state == SEE:
            self.track.append(self.pos[:])


        self.screen.set(PLAYER, *self.pos)

    def loose_back(self):
        self.state = LAND
        self.screen.make_see(self.track)
        self.pos = self.see_start[:]

    def fill_new_land(self):
        for p in self.track:
            self.screen.set(LAND, *p)
        self.screen.fill_new_land()
                

def init_reflectors(screen):
    reflectors = []
    for i in (1,2,3):
        x = int(random.random()*(screen.maxX-10)) + 5
        y = int(random.random()*(screen.maxY-10)) + 5
        reflectors.append(ReflectingPoint(screen, x, y, SEE, (LAND, OVERBOARD)))
    return reflectors

                
def reflect_test(stdscr):
    screen = Screen(stdscr)
    screen.fill_init()
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


def main(stdscr):
    screen = Screen(stdscr)
    screen.fill_init()
    reflectors = init_reflectors(screen)
    screen.monsters = reflectors
    player = Player(screen, 0,0)
    while True:
        for r in reflectors:
            r.move()
        screen.refresh()   
        if STATE.state == 'loose':
            player.loose_back()
        time.sleep(0.04)
        c = screen.getch()
        while screen.getch() != -1:
            pass
        if c == curses.KEY_UP:        player.move('up')
        elif c == curses.KEY_DOWN:      player.move('down')
        elif c == curses.KEY_LEFT:      player.move('left')
        elif c == curses.KEY_RIGHT:     player.move('right')






if __name__ == '__main__':
#    curses.wrapper(reflect_test)
    curses.wrapper(main)
