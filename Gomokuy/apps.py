#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Flask, render_template, request, redirect, url_for
from gomokuy import Gomokuy
from base import B, W
import logging


app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route("/")
def home():
    loc = request.args.get('loc')
    retract, restart = request.args.get('retract'), request.args.get('restart')
    if restart:
        fir = request.args.get('aifirst')
        if fir == "1":
<<<<<<< HEAD
            game.move((7, 7))
        return redirect(url_for("home"))
    if retract and retract == "1":
        # 悔棋
        game.undo(counts=2)
=======
            game.restart(role=B)
        else:
            game.restart(role=W)
        return redirect(url_for("home"))
    if retract and retract == "1":
        # 悔棋
        game.undo()
>>>>>>> origin/master
        return redirect(url_for("home"))

    if not loc:
        # 第一次打开，直接开始新游戏
        return render_template("home.html", game=game)
    # 玩家下一步棋开始
    loc = int(loc)
    pos = (int(loc / game.width), int(loc % game.width))
    game.move(pos)
    # 玩家下一步棋结束

    # 电脑下一步棋开始
    if True:
        m_pos = game.min_max_search(DEEPS=2)
    elif len(game.records) <= 16:
        m_pos = game.min_max_search(DEEPS=6)
    else:
        m_pos = game.min_max_search(DEEPS=12)
    if m_pos:
        game.move(m_pos)

    # 电脑下一步棋结束
    return redirect(request.referrer)


if __name__ == '__main__':
    game = Gomokuy()
    app.run(host="0.0.0.0", debug=True)
