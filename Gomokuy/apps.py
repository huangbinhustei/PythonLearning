#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import queue
from queue import Queue
import logging
import threading
import time
from tkinter import *

from gomokuy import Gomokuy

logger = logging.getLogger('Gomoku')
logger.setLevel(logging.WARNING)
que_game2ui = Queue(maxsize=2)
que_ui2game = Queue(maxsize=2)

GUI_CONF = {
    "gap": 30,  # 棋盘间隔
    "half_gap": 15,  # 棋盘间隔的一半，用于识别点击位置
    "flag": 12,  # 棋子半径
    "stress": 2,  # 棋子中用来强调的标记的半径
}


class GAME(Gomokuy):
    def __init__(self, restricted=True, ai=False, difficulty=4):
        """
        :param restricted: 是否支持悔棋，True/False
        :param ai: ai执黑还是执白，假如是PVP或者录入题目，ai=False
        :param difficulty: 思考深度
        """
        print('Thread (%s) start in GAME' % threading.currentThread().getName())

        self.ai = ai
        self.difficulty = difficulty
        Gomokuy.__init__(self, settle=False, restricted=restricted)
        if ai == "Black":
            self.move((7, 7))
            que_game2ui.put({
                "game": self,
                "info": "move"})

        self.queue_handler()

    def restart(self, restricted=True, ai="Black", difficulty=4):
        logger.info("重启游戏")
        self.__init__(restricted=restricted, ai=ai, difficulty=difficulty)

    def solve(self):
        print("Begin Solve")
        self.settle = True
        pos = self.iterative_deepening(7)
        print(f"The Best Choice is {pos}")
        self.move(pos)
        que_game2ui.put({
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
        que_game2ui.put({
            "game": self,
            "info": "move"})

    def queue_handler(self):
        while True:
            try:
                task = que_ui2game.get(block=False)
                if task["option"] == "move":
                    row, col = task["loc"]
                    self.moving(row, col)
                elif task["option"] == "restart":
                    self.restart()
                elif task["option"] == "solve":
                    self.solve()
                elif task["option"] == "undo":
                    self.undo_in_use()
                time.sleep(1)
            except queue.Empty:
                time.sleep(0.1)

    def moving(self, row, col):
        if self.winner:
            print("游戏结束")
            return

        ret = self.move((row, col))
        if ret:
            que_game2ui.put({
                "game": self,
                "info": "move"}, block=False)
            print(f"first put\tsize={que_game2ui.qsize()} @ {time.ctime()}")
            if not self.ai:
                return
            pos2 = self.iterative_deepening(self.difficulty)
            if pos2:
                self.move(pos2)
                que_game2ui.put({
                    "game": self,
                    "info": "move"}, block=False)
                print(f"second put\tsize={que_game2ui.qsize()} @ {time.ctime()}")
        else:
            que_game2ui.put({
                "game": self,
                "info": "Game Over"})


class GUI:
    def __init__(self, ui):
        print('Thread (%s) start in GUI' % threading.currentThread().getName())
        print("GUI打开")

        self.bg = Canvas(ui, width=GUI_CONF["gap"] * 16, height=GUI_CONF["gap"] * 16, bg="white")
        self.bg_draw()
        self.bg.grid(row=0, column=0, sticky=E)
        self.bg.bind("<Button-1>", self.on_click)

        self.btn_solve = Button(ui, text="解题", command=lambda: que_ui2game.put({"option": "solve"}))
        self.btn_solve.grid(row=1, column=0, sticky=E)
        self.btn_restart = Button(ui, text="重启", command=lambda: que_ui2game.put({"option": "restart"}))
        self.btn_restart.grid(row=1, column=1, sticky=E)
        self.btn_undo = Button(ui, text="悔棋", command=lambda: que_ui2game.put({"option": "undo"}))
        self.btn_undo.grid(row=1, column=2, sticky=E)
        menu = Menu(ui)
        for item in ["文件", "设置", "关于"]:
            menu.add_command(label=item)

        ui.title("Gomokuy")
        ui["menu"] = menu

        self.queue_handler()

    def on_click(self, event):
        col = (event.x + GUI_CONF["half_gap"]) // GUI_CONF["gap"] - 1
        row = (event.y + GUI_CONF["half_gap"]) // GUI_CONF["gap"] - 1
        que_ui2game.put({
            "option": "move",
            "loc": (row, col),
        })

    def renew(self):
        self.bg.delete(ALL)
        self.bg_draw()

    def bg_draw(self):
        for row in range(1, 16):
            self.bg.create_line(row * GUI_CONF["gap"], GUI_CONF["gap"],
                                row * GUI_CONF["gap"], GUI_CONF["gap"] * 15,
                                fill="black", width=1)
            self.bg.create_line(GUI_CONF["gap"], row * GUI_CONF["gap"],
                                GUI_CONF["gap"] * 15, row * GUI_CONF["gap"],
                                fill="black", width=1)
        self.bg.grid(row=0, column=0)

    def circle_draw(self, row, col, r, **kwargs):
        x = (col + 1) * GUI_CONF["gap"]
        y = (row + 1) * GUI_CONF["gap"]
        return self.bg.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def queue_handler(self):
        try:
            task = que_game2ui.get(block=False)
            self.renew()
            game = task["game"]
            print(f"{game.step}\t{time.ctime()}")
            for row, line in enumerate(task["game"].table):
                for col, cell in enumerate(line):
                    if cell == 0:
                        continue
                    color = "white" if cell == 2 else "black"
                    self.circle_draw(row, col, GUI_CONF["flag"], fill=color)
                    if (row, col) in task["game"].check:
                        self.circle_draw(row, col, GUI_CONF["stress"], fill="red")
                    if (row, col) == task["game"].records[-1]:
                        self.circle_draw(row, col, GUI_CONF["stress"], fill="green")
            self.bg.after(1, self.queue_handler)
        except queue.Empty:
            self.bg.after(1, self.queue_handler)


if __name__ == '__main__':
    window = Tk()
    gui = GUI(window)
    t1 = threading.Thread(target=GAME, args=(window,))
    t1.setDaemon = True
    t1.start()
    window.mainloop()
