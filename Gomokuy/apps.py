#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Flask, render_template, request, redirect, url_for
from gomokuy import Gomokuy
import logging


app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route("/")
def home():
    loc = request.args.get('loc')
    retract, restart= request.args.get('retract'), request.args.get('restart')
    if restart:
        print("重启游戏")
        game.restart()
        fir = request.args.get('aifirst')
        if fir == "1":
            game.move((7, 7))
        return redirect(url_for("home"))
    if retract and retract == "1":
        # 悔棋
        game.undo()
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
    # m_pos = game.analyse()
    if len(game.records) <= 8:
        m_pos = game.min_max_search(DEEPS=3)
    elif len(game.records) <= 16:
        m_pos = game.min_max_search(DEEPS=5)
    else:
        m_pos = game.min_max_search(DEEPS=7)
    if m_pos:
        game.move(m_pos)

    # 电脑下一步棋结束
    return redirect(request.referrer)


if __name__ == '__main__':
    print("游戏开始")
    game = Gomokuy()
    app.run(host="0.0.0.0", debug=True)
