#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Flask, render_template, request, redirect, url_for
from gomokuy import Gomokuy
import logging
from tkinter import *


app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
logger = logging.getLogger('Gomoku')


class TFace(Gomokuy):
    def __init__(self, restricted=True, ai_first=False, difficulty=4, pve=True):
        Gomokuy.__init__(self, settle=False, restricted=restricted)
        self.difficulty = difficulty
        self.pve = pve
        self.desktop = Tk()
        self.c = Canvas(self.desktop, width=480, height=480, bg="white")
        for row in range(1, 16):
            self.c.create_line(row * 30, 30, row * 30, 450, fill="black", width=1)
            self.c.create_line(30, row * 30, 450, row * 30, fill="black", width=1)

        self.c.bind("<Button-1>", self.on_click)
        self.c.grid(row=0, column=0)
        self.b_solve = Button(self.desktop, text="解题", command=self.solve)
        self.b_restart = Button(self.desktop, text="重启", command=self.restart)
        self.b_solve.grid(row=0, column=1, sticky=W)
        self.b_restart.grid(row=1, column=1, sticky=W)

        self.btn_cccc = Button(self.desktop, text="清空", command=(lambda: self.c.delete(ALL)))
        self.btn_cccc.grid(row=2, column=1, sticky=W)

        self.desktop.title("Gomokuy")

        menu = Menu(self.desktop)
        for item in ["文件", "设置", "关于"]:
            menu.add_command(label=item)
        self.desktop["menu"] = menu
        self.desktop.mainloop()

    def restart(self, restricted=True, ai_first=False, difficulty=4):
        print("重启游戏")
        self.__init__(restricted=restricted, ai_first=ai_first, difficulty=difficulty)

    def solve(self):
        ret = self.iterative_deepening(7)
        if ret:
            col, row = ret
            self.draw_circle(row * 30 + 30, col * 30 + 30, 12, fill="green")

    def on_click(self, event):
        if self.winner:
            print("游戏结束")
            return
        row = (event.x + 15) // 30 - 1
        col = (event.y + 15) // 30 - 1

        offset = (event.x % 30, event.y % 30)
        print(f"{(event.x, event.y)}\t{(row, col)}\t{offset}")

        color = {True: "white", False: "black"}[len(self.records) % 2]
        ret = self.move((col, row))
        # 这个略 trick， 游戏里面的row其实是列。

        if not ret:
            return
        self.draw_circle(row * 30 + 30, col * 30 + 30, 12, fill=color)

        if self.pve:
            ret = self.iterative_deepening(self.difficulty)
            if ret:
                color = {True: "white", False: "black"}[len(self.records) % 2]
                col, row = ret
                self.move((col, row))
                self.draw_circle(row * 30 + 30, col * 30 + 30, 12, fill=color)

    def draw_circle(self, x, y, r, **kwargs):
        return self.c.create_oval(x - r, y - r, x + r, y + r, **kwargs)


class PVE(Gomokuy):
    def __init__(self, restricted=True, ai_first=False, difficulty=4):
        Gomokuy.__init__(self, settle=False, restricted=restricted)
        if ai_first:
            self.move((7, 7), show=True)

        self.ai_first = ai_first
        self.difficulty = difficulty
        logger.info("游戏开始")

    def restart(self, restricted=True, ai_first=False, difficulty=4):
        logger.info("重启游戏")
        self.__init__(restricted=restricted, ai_first=ai_first, difficulty=difficulty)

    def round(self, pos):
        self.move(pos)
        ai_pos = game.iterative_deepening(self.difficulty)
        if ai_pos:
            game.move(ai_pos, show=True)

    def undo_in_use(self):
        # 以白棋走，悔棋悔到偶数
        if (not self.step % 2) and self.ai_first:
            self.undo(count=1)
        else:
            self.undo(count=2)


@app.route("/")
def home():
    loc = request.args.get('loc')
    retract, restart = request.args.get('retract'), request.args.get('restart')
    ai_first = (request.args.get("aifirst") == "True")
    if restart:
        game.restart(ai_first=ai_first)
        return redirect(url_for("home"))
    if retract and retract == "1":
        # 悔棋
        game.undo_in_use()
        return redirect(url_for("home"))
    if not loc:
        # 第一次打开，直接开始新游戏
        return render_template("home.html", game=game)

    loc = int(loc)
    pos = (int(loc / game.width), int(loc % game.width))
    game.round(pos)

    return redirect(request.referrer)


if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    game = PVE()
    app.run(host="0.0.0.0", debug=True)
