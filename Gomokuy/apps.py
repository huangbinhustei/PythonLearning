#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import queue
import logging
import threading
import time
import os
from tkinter import *

from gomokuy import Gomokuy

logger = logging.getLogger('Gomoku')
logger.setLevel(logging.WARNING)


class PVE(threading.Thread, Gomokuy):
    def __init__(self, ui, q, pve=True):
        # threading.Thread.__init__(self)
        print('Process (%s) start in PVE' % threading.currentThread().getName())
        Gomokuy.__init__(self)
        self.gui = ui
        self.queue = q
        self.pve = pve
        # self.daemon = True
        # self.start()
        self.gui.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        if self.winner:
            print("游戏结束")
            return
        col = (event.x + 15) // 30 - 1
        row = (event.y + 15) // 30 - 1

        ret = self.move((row, col))
        if ret:
            self.queue.put({
                "game": self,
                "info": "move"})
            print("before" + str(time.ctime()))
            if not self.pve:
                return
            pos2 = self.iterative_deepening(3)
            if pos2:
                self.move(pos2)
                self.queue.put({
                    "game": self,
                    "info": "move"})
            print("after" + str(time.ctime()))
        else:
            self.queue.put({
                "game": self,
                "info": "Game Over"})


class GUI():
    def __init__(self, ui, q):
        print('Process (%s) start in GUI' % threading.currentThread().getName())
        print("GUI打开")
        self.queue = q
        self.ui = ui
        self.bg = Canvas(self.ui, width=480, height=480, bg="white")
        self.bg_draw()

        # self.btn_solve = Button(self, text="解题", command=self.solve)
        # self.btn_solve.grid(row=0, column=1, sticky=W)
        # 支持EVE 之后，才有解题的必要

        # self.btn_restart = Button(self, text="重启", command=self.restart)
        # self.btn_restart.grid(row=1, column=1, sticky=W)

        self.ui.title("Gomokuy")
        self.queue_handler()

    def renew(self):
        self.bg.delete(ALL)
        self.bg_draw()

    def bg_draw(self):
        for row in range(1, 16):
            self.bg.create_line(row * 30, 30, row * 30, 450, fill="black", width=1)
            self.bg.create_line(30, row * 30, 450, row * 30, fill="black", width=1)
        self.bg.grid(row=0, column=0)

    def circle_draw(self, x, y, r, **kwargs):
        return self.bg.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def queue_handler(self):
        try:
            task = self.queue.get(block=False)
            self.renew()
            for row, line in enumerate(task["game"].table):
                for col, cell in enumerate(line):
                    if cell == 0:
                        continue
                    color = "white" if cell == 2 else "black"
                    self.circle_draw(col * 30 + 30, row * 30 + 30, 12, fill=color)
                    if (row, col) in task["game"].check:
                        self.circle_draw(col * 30 + 30, row * 30 + 30, 6, fill="red")
                    if (row, col) == task["game"].records[-1]:
                        self.circle_draw(col * 30 + 30, row * 30 + 30, 6, fill="yellow")
            self.bg.after(10, self.queue_handler)
        except queue.Empty:
            self.bg.after(10, self.queue_handler)


if __name__ == '__main__':
    window = Tk()
    que = queue.Queue(maxsize=2)
    gui = GUI(window, que)
    game = PVE(window, que)
    window.mainloop()
    
