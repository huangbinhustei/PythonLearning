#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import queue
import logging
import threading
import time
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


class GAME(Gomokuy):
    def __init__(self, _gui, que_game2ui, que_ui2game,
                 restricted=True, ai="White", difficulty=1):
        """
        :param _gui:
        :param que_game2ui:
        :param que_ui2game:
        :param restricted: 是否支持悔棋，True/False
        :param ai: ai执黑还是执白，假如是PVP或者录入题目，ai=False
        :param difficulty: 思考深度
        """

        self.gui = _gui
        self.que_game2ui = que_game2ui
        self.que_ui2game = que_ui2game
        self.queue_handler()

        self.ai = ai
        self.difficulty = difficulty
        Gomokuy.__init__(self, settle=False, restricted=restricted)
        if ai == "Black":
            self.move((7, 7))
            self.que_game2ui.put({
                "game": self,
                "info": "move"})

    def restart(self, restricted=True, ai="Black", difficulty=2):
        logger.info("重启游戏")
        self.__init__(self.gui, self.que_game2ui, self.que_ui2game,
                      restricted=restricted, ai=ai, difficulty=difficulty)

    def solve(self):
        pos = self.iterative_deepening(7)
        self.move(pos)
        self.que_game2ui.put({
            "game": self,
            "info": "move"})

    def undo_in_use(self):
        # 以白棋走，悔棋悔到偶数
        if not self.ai:
            count = 1
        elif self.ai == "Black":
            count = 2 if self.step % 2 else 1
        elif self.ai == "White":
            count = 1 if self.step % 2 else 2
        Gomokuy.undo(self, count=count)
        self.que_game2ui.put({
            "game": self,
            "info": "move"})

    def queue_handler(self):
        try:
            task = self.que_ui2game.get(block=False)
            if task["option"] == "move":
                row, col = task["loc"]
                self.moving(row, col)
            elif task["option"] == "restart":
                self.restart()
            elif task["option"] == "solve":
                self.solve()
            elif task["option"] == "undo":
                self.undo_in_use()

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
            if not self.ai:
                return
            f = time.time()
            pos2 = self.iterative_deepening(self.difficulty)
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
        self.btn_solve.grid(row=1, column=0, sticky=E)
        self.btn_restart = Button(self.ui, text="重启", command=self.restart)
        self.btn_restart.grid(row=1, column=1, sticky=E)
        self.btn_undo = Button(self.ui, text="悔棋", command=self.undo)
        self.btn_undo.grid(row=1, column=2, sticky=E)

        self.queue_handler()

    def undo(self):
        self.que_ui2game.put({
            "option": "undo",
        })

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
        self.circle_draw(row, col, GUICONF["flag"], fill=color)

    def renew(self):
        self.bg.delete(ALL)
        self.bg_draw()

    def bg_draw(self):
        for row in range(1, 16):
            self.bg.create_line(row * GUICONF["gap"], GUICONF["gap"],
                                row * GUICONF["gap"], GUICONF["gap"] * 15,
                                fill="black", width=1)
            self.bg.create_line(GUICONF["gap"], row * GUICONF["gap"],
                                GUICONF["gap"] * 15, row * GUICONF["gap"],
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
    q_game2ui = queue.Queue(maxsize=2)
    q_ui2game = queue.Queue(maxsize=2)
    gui = GUI(window, q_game2ui, q_ui2game)
    t1 = threading.Thread(target=GAME, args=(window, q_game2ui, q_ui2game))
    t1.daemon = True
    t1.start()
    window.mainloop()
