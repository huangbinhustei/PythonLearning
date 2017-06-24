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
    retract = request.args.get('retract')
    restart = request.args.get('restart')
    if restart:
        print("重启游戏")
        game.restart()
        fir = request.args.get('aifirst')
        if fir == "1":
            game.going((7, 7))
        return redirect(url_for("home"))
    if retract and retract == "1":
        # 悔棋
        game.retract()
        return redirect(url_for("home"))

    if not loc:
        # 第一次打开，直接开始新游戏
        return render_template("home.html", game=game)
    # 玩家下一步棋开始
    loc = int(loc)
    pos = (int(loc / game.width), int(loc % game.width))
    game.going(pos)
    # 玩家下一步棋结束

    # 电脑下一步棋开始
    m_pos = game.analyse()
    game.going(m_pos)

    # 电脑下一步棋结束
    return redirect(request.referrer)


if __name__ == '__main__':
    print("游戏开始")
    game = Gomokuy()
    app.run(host="0.0.0.0", debug=True)
