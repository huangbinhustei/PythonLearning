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

GUICONF = {
    "gap": 40,  # 棋盘间隔
    "half_gap": 20,  # 棋盘间隔的一半，用于识别点击位置
    "flag": 16,  # 棋子半径
    "stress": 6,  # 棋子中用来强调的标记的半径
}


class PVE(Gomokuy):
    def __init__(self, gui, que_game2ui, que_ui2game,
                 pve=True, restricted=True, ai_first=False, difficulty=4):
        print('Thread (%s) start in PVE' % threading.currentThread().getName())
        Gomokuy.__init__(self, settle=False, restricted=restricted)

        if ai_first:
            self.moving(7, 7)
        self.ai_first = ai_first

        self.difficulty = difficulty
        self.gui = gui
        self.que_game2ui = que_game2ui
        self.que_ui2game = que_ui2game
        self.pve = pve
        self.queue_handler()

    def restart(self, restricted=True, ai_first=False, difficulty=4):
        logger.info("重启游戏")
        Gomokuy.__init__(self, settle=False, restricted=restricted)
        if ai_first:
            self.moving(7, 7)
        self.ai_first = ai_first
        self.difficulty = difficulty

    def queue_handler(self):
        try:
            task = self.que_ui2game.get(block=False)
            if task["option"] == "move":
                row, col = task["loc"]
                self.moving(row, col)
            elif task["option"] == "restart":
                print("restart in PVE")
                self.restart()
            elif task["option"] == "solve":
                print("solve in PVE")

            self.gui.after(10, self.queue_handler)
        except queue.Empty:
            self.gui.after(10, self.queue_handler)

    def moving(self, row, col):
        if self.winner:
            print("游戏结束")
            return

        ret = self.move((row, col))
        if ret:
            self.que_game2ui.put({
                "game": self,
                "info": "move"})
            if not self.pve:
                return
            f = time.time()
            pos2 = self.iterative_deepening(1)
            print(time.time() - f)
            if pos2:
                self.move(pos2)
                self.que_game2ui.put({
                    "game": self,
                    "info": "move"})

        else:
            self.que_game2ui.put({
                "game": self,
                "info": "Game Over"})


class GUI:
    def __init__(self, ui, que_game2ui, que_ui2game):
        print('Thread (%s) start in GUI' % threading.currentThread().getName())
        print("GUI打开")
        self.que_game2ui = que_game2ui
        self.que_ui2game = que_ui2game
        self.game = ""

        self.ui = ui
        self.bg = Canvas(self.ui, width=GUICONF["gap"] * 16, height=GUICONF["gap"] * 16, bg="white")
        self.bg_draw()
        self.ui.title("Gomokuy")
        self.ui.bind("<Button-1>", self.on_click)
        self.btn_solve = Button(self.ui, text="解题", command=self.solve)
        self.btn_solve.grid(row=0, column=1, sticky=W)
        self.btn_restart = Button(self.ui, text="重启", command=self.restart)
        self.btn_restart.grid(row=1, column=1, sticky=W)

        self.queue_handler()

    def solve(self):
        self.que_ui2game.put({
            "option": "solve",
        })

    def restart(self):
        self.renew()
        self.que_ui2game.put({
            "option": "restart",
        })

    def on_click(self, event):
        print(time.ctime())
        col = (event.x + GUICONF["half_gap"]) // GUICONF["gap"] - 1
        row = (event.y + GUICONF["half_gap"]) // GUICONF["gap"] - 1
        self.que_ui2game.put({
            "option": "move",
            "loc": (row, col),
        })

        if not self.game:
            color = "black"
        elif self.game.winner:
            return
        elif self.game.step % 2 == 0:
            color = "black"
        else:
            color = "white"
        print(time.ctime())
        self.circle_draw(row, col, GUICONF["flag"], fill=color)
        print(time.ctime())

    def renew(self):
        self.bg.delete(ALL)
        self.bg_draw()

    def bg_draw(self):
        for row in range(1, 16):
            self.bg.create_line(row * GUICONF["gap"], GUICONF["gap"], row * GUICONF["gap"], GUICONF["gap"] * 15,
                                fill="black", width=1)
            self.bg.create_line(GUICONF["gap"], row * GUICONF["gap"], GUICONF["gap"] * 15, row * GUICONF["gap"],
                                fill="black", width=1)
        self.bg.grid(row=0, column=0)

    def circle_draw(self, row, col, r, **kwargs):
        x = (col + 1) * GUICONF["gap"]
        y = (row + 1) * GUICONF["gap"]
        return self.bg.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def queue_handler(self):
        try:
            task = self.que_game2ui.get(block=False)
            self.renew()
            self.game = task["game"]
            for row, line in enumerate(task["game"].table):
                for col, cell in enumerate(line):
                    if cell == 0:
                        continue
                    color = "white" if cell == 2 else "black"
                    self.circle_draw(row, col, GUICONF["flag"], fill=color)
                    if (row, col) in task["game"].check:
                        self.circle_draw(row, col, GUICONF["stress"], fill="red")
                    if (row, col) == task["game"].records[-1]:
                        self.circle_draw(row, col, GUICONF["stress"], fill="green")
            self.bg.after(10, self.queue_handler)
        except queue.Empty:
            self.bg.after(10, self.queue_handler)


if __name__ == '__main__':
    window = Tk()
    que_game2ui = queue.Queue(maxsize=2)
    que_ui2game = queue.Queue(maxsize=2)
    gui = GUI(window, que_game2ui, que_ui2game)
    t1 = threading.Thread(target=PVE, args=(window, que_game2ui, que_ui2game))
    t1.daemon = True
    t1.start()
    window.mainloop()
