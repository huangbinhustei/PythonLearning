#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Flask, render_template, request, redirect, url_for
from gomokuy import Gomokuy
import logging


app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
logger = logging.getLogger('Gomoku')
count = 1


def pvp(pos):
    ret = 1
    game.move(pos)

    # 电脑下一步棋开始
    g_pos = game.iterative_deepening(4)
    if g_pos:
        ret += 1
        game.move(g_pos, show=True)
    # 电脑下一步棋结束
    return ret


@app.route("/")
def home():
    global count
    loc = request.args.get('loc')
    retract, restart= request.args.get('retract'), request.args.get('restart')
    if restart:
        logger.info("重启游戏")
        game.restart()
        fir = request.args.get('aifirst')
        if fir == "1":
            game.move((7, 7), show=True)
        return redirect(url_for("home"))
    if retract and retract == "1":
        # 悔棋
        game.undo(count=count)
        return redirect(url_for("home"))
    if not loc:
        # 第一次打开，直接开始新游戏
        return render_template("home.html", game=game)

    loc = int(loc)
    pos = (int(loc / game.width), int(loc % game.width))
    count = pvp(pos)

    return redirect(request.referrer)


if __name__ == '__main__':
    game = Gomokuy()
    logger.setLevel(logging.INFO)
    logger.info("游戏开始")
    app.run(host="0.0.0.0", debug=True)
