#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from renju import Renjuy
import logging
import time
from tkinter import *

logger = logging.getLogger('Gomoku')
logger.setLevel(logging.WARNING)


class EVEV2(Renjuy):
    def __init__(self):
        Renjuy.__init__(self)
        self.desktop = Tk()
        self.c = Canvas(self.desktop, width = 480, height = 480, bg = "white")
        self.c.pack()
        for row in range(1, 16):
            self.c.create_line(row * 30, 30, row * 30, 450, fill="black", width=1)
            self.c.create_line(30, row * 30, 450, row * 30, fill="black", width=1)
        # self.desktop.mainloop()
        self.work = Canvas(self.desktop, width=480, height=480)
        self.work.pack(expand=YES, fill=BOTH)
        self.work.bind("<Button-1>", self.on_click)


    def on_click(self):
        self.drawCircle(510, 620, 24, fill="yello")

    def drawCircle(self, x, y, r, **kwargs):
        return self.c.create_oval(x-r, y-r, x+r, y+r, **kwargs)

    def get_pos(self):
        d = {True: 1, False: 1}[len(self.records) % 2]
        # True: 白， False: 黑
        return self.iterative_deepening(d)

    def show(self):
        for row in range(15):
            for col in range(15):
                if self.table[row][col] == 0:
                    continue
                if self.table[row][col] == 1:
                    self.drawCircle(row * 30 + 30, col * 30 + 30, 12, fill="black")
                if self.table[row][col] == 2:
                    self.drawCircle(row * 30 + 30, col * 30 + 30, 12, fill="white")
        self.desktop.mainloop()

    def new_show(self, pos):
        color = {True: "white", False: "black"}[len(self.records) % 2]
        row, col = pos
        self.drawCircle(row * 30 + 30, col * 30 + 30, 12, fill=color)
        self.c.pack()
        


    def run(self):
        self.move((7, 7))
        self.new_show((7, 7))
        while not self.winner:
            pos = self.get_pos()
            if pos:
                self.move(pos)
                self.new_show(pos)
            else:
                break
        print(f"\n总共 {game.step} 步！！")
        self.show()
        


class EVE(Renjuy):
    def __init__(self):
        self.black = Renjuy()
        self.white = Renjuy()
        self.black.move((7, 7))
        self.white.move((7, 7))
        # self.black.score  = {
        #     "冲6": 10000,
        #     "冲5": 10000,
        #     "活4": 10000,
        #     "冲4": 500,
        #     "活3": 100,
        #     "冲3": 20,
        #     "活2": 10,
        #     "冲2": 1,
        #     "活1": 1,
        #     "冲1": 0,
        #     "禁手": -100,
        # }
        # self.white.score  = {
        #     "冲6": 100000,
        #     "冲5": 100000,
        #     "活4": 100000,
        #     "冲4": 1000,
        #     "活3": 1000,
        #     "冲3": 10,
        #     "活2": 10,
        #     "冲2": 1,
        #     "活1": 1,
        #     "冲1": 0,
        #     "禁手": -100,
        # }

    def round(self):
        w_pos = self.white.iterative_deepening(1)
        if w_pos:
            self.white.move(w_pos)
            self.black.move(w_pos)
        b_pos = self.black.iterative_deepening(1)
        if b_pos:
            self.white.move(b_pos)
            self.black.move(b_pos)

    def run(self):
        while not game.white.winner:
            game.round()
        print(f"\n总共 {game.white.step} 步！！")



if __name__ == '__main__':
    game = EVEV2()
    # game = EVE()

    start = time.time()
    game.run()
    print(time.time() - start)
    
   
