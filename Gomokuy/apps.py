#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Flask, render_template, request, redirect, url_for
from gomokuy import Gomokuy
import logging


app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
logger = logging.getLogger('Gomoku')


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
