#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import queue
# from queue import Queue
import logging
import threading
import time
from tkinter import *

from base import show_timing, PRINTING, cost_dict, Renjuy

logger = logging.getLogger('Renju')
logger.setLevel(logging.DEBUG)
que_game2ui = queue.Queue(maxsize=2)
que_ui2game = queue.Queue(maxsize=2)

GUI_CONF = {
    "gap": 30,  # 棋盘间隔
    "half_gap": 15,  # 棋盘间隔的一半，用于识别点击位置
    "flag": 12,  # 棋子半径
    "stress": 2,  # 棋子中用来强调的标记的半径
}


class GAME(Renjuy):
    def __init__(self, ai=False, difficulty=3):
        """
        :param ai: ai执黑还是执白（执黑 ai="Black"），假如是PVP或者录入题目，ai=False
        :param difficulty: 思考深度
        """
        logger.info('Thread (%s) start in GAME' % threading.currentThread().getName())

        self.ai = ai
        self.difficulty = difficulty

        Renjuy.__init__(self, forbidden=True)
        if ai == "Black":
            self.move((7, 7))
            que_game2ui.put({
                "game": self,
                "info": "move"})

        self.queue_handler()

    def restart(self, restricted=True, ai=False, difficulty=3):
        logger.info("重启游戏")
        cost_dict.clear()
        self.__init__(ai=ai, difficulty=difficulty)

    def solve(self):
        if self.step <= 5:
            pos, fen = self.iterative_deepening(1)
        elif self.step <= 9:
            pos, fen = self.iterative_deepening(2)
        else:
            pos, fen = self.iterative_deepening(self.difficulty)
        show_timing()
        logger.info(f"The Best Choice is {pos}")
        self.move(pos)
        que_game2ui.put({
            "game": self,
            "info": "move"})

    def undo_in_use(self):
        Renjuy.undo(self)
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
                elif task["option"] == "debug":
                    self.show_situation()
                time.sleep(0.1)
            except queue.Empty:
                time.sleep(0.1)

    def moving(self, row, col):
        if self.winner != 2:
            logger.info("游戏结束")
            return

        ret = self.move((row, col))
        if ret:
            que_game2ui.put({
                "game": self,
                "info": "move"}, block=False)
            # logger.debug(f"first put\tsize={que_game2ui.qsize()} @ {time.ctime()}")
            if not self.ai:
                return
            pos2, fen2 = self.iterative_deepening(self.difficulty)
            if pos2:
                self.move(pos2)
                que_game2ui.put({
                    "game": self,
                    "info": "move"}, block=False)
                # logger.debug(f"second put\tsize={que_game2ui.qsize()} @ {time.ctime()}")
        else:
            que_game2ui.put({
                "game": self,
                "info": "Game Over"})

    def show_situation(self):
        Renjuy.show_situation(self)
        print(self.forced)
        tt = ["零一二三四五六七八九ABCDE"[x[0]] + "0123456789abcde"[x[1]] for x in self.candidates]
        logger.info(f"{PRINTING[self.step % 2]}方选点：{tt}")
        que_game2ui.put({
            "game": self,
            "info": "debug"}, block=False)


class GUI:
    def __init__(self, ui):
        print('Thread (%s) start in GUI' % threading.currentThread().getName())
        print("GUI打开")

        self.bg = Canvas(ui,
                         width=GUI_CONF["gap"] * 16,
                         height=GUI_CONF["gap"] * 15 + GUI_CONF["flag"],
                         bg="white")
        self.__bg_draw()
        self.bg.grid(row=10, columnspan=8, sticky=E)
        self.bg.bind("<Button-1>", self.on_click)

        tmp_h = "    ".join(["      0", " 1", "  2", " 3", "  4", " 5", "  6",
                             " 7", "  8", " 9", "10", "11", "12", "13", "14"])
        self.label_h = Label(text=tmp_h)
        self.label_h.grid(row=11, columnspan=8, sticky=W)

        tmp_v = "\n".join(["\n零", "\n一", "\n二", "\n三", "\n四", "\n五", "\n六",
                           "\n七", "\n八", "\n九", "\n十", "\nB", "\nC", "\nD", "\nE"])
        self.label_h = Label(text=tmp_v, font=("Helvetica", 13))
        self.label_h.grid(row=10, columnspan=9, sticky=W)

        self.btn_solve = Button(ui, text="解题", command=lambda: que_ui2game.put({"option": "solve"}))
        self.btn_solve.grid(row=15, column=0, sticky=N)
        self.btn_restart = Button(ui, text="重启", command=lambda: que_ui2game.put({"option": "restart"}))
        self.btn_restart.grid(row=15, column=1, sticky=N)
        self.btn_undo = Button(ui, text="悔棋", command=lambda: que_ui2game.put({"option": "undo"}))
        self.btn_undo.grid(row=15, column=2, sticky=N)
        self.btn_debug = Button(ui, text="调试", command=lambda: que_ui2game.put({"option": "debug"}))
        self.btn_debug.grid(row=15, column=3, sticky=N)

        ui.title("Gomokuy")

        self.queue_handler()

    def __bg_draw(self):
        for row in range(1, 16):
            self.bg.create_line(row * GUI_CONF["gap"], GUI_CONF["gap"],
                                row * GUI_CONF["gap"], GUI_CONF["gap"] * 15,
                                fill="black", width=1)
            self.bg.create_line(GUI_CONF["gap"], row * GUI_CONF["gap"],
                                GUI_CONF["gap"] * 15, row * GUI_CONF["gap"],
                                fill="black", width=1)
            self.bg.grid(row=10, columnspan=8, sticky=E)

    def __placing(self, row, col, r, **kwargs):
        x = (col + 1) * GUI_CONF["gap"]
        y = (row + 1) * GUI_CONF["gap"]
        return self.bg.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def queue_handler(self):
        try:
            task = que_game2ui.get(block=False)
            self.__renew()
            game = task["game"]
            # logger.debug(f"{game.step}\t{time.ctime()}")
            for row, line in enumerate(game.table):
                for col, cell in enumerate(line):
                    if cell == 2:
                        if task["info"] == "debug" and (row, col) in game.candidates:
                            # 调试信息：
                            self.__placing(row, col, GUI_CONF["flag"]//2, fill="yellow")
                        continue
                    color = "white" if cell == 1 else "black"
                    self.__placing(row, col, GUI_CONF["flag"], fill=color)
                    # if (row, col) in task["game"].check:
                    #     self.circle_draw(row, col, GUI_CONF["stress"], fill="red")
                    if (row, col) == task["game"].records[-1]:
                        self.__placing(row, col, GUI_CONF["stress"], fill="green")
            self.bg.after(1, self.queue_handler)
        except queue.Empty:
            self.bg.after(1, self.queue_handler)

    def on_click(self, event):
        col = (event.x + GUI_CONF["half_gap"]) // GUI_CONF["gap"] - 1
        row = (event.y + GUI_CONF["half_gap"]) // GUI_CONF["gap"] - 1
        que_ui2game.put({
            "option": "move",
            "loc": (row, col),
        })

    def __renew(self):
        self.bg.delete(ALL)
        self.__bg_draw()


if __name__ == '__main__':
    window = Tk()
    gui = GUI(window)
    t1 = threading.Thread(target=GAME, args=(False, 3))
    t1.setDaemon = True
    t1.start()
    window.mainloop()
