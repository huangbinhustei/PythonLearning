#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Flask, render_template, request, redirect
from gomoku import Calc

app = Flask(__name__)


@app.route("/")
def home():
    loc = request.args.get('loc')
    if game.over:
        game.restart()
        return render_template("home.html", game=game)
    if not loc:
        return render_template("home.html", game=game)
    # 玩家下一步棋开始
    loc = int(loc)
    pos = (int(loc / game.width), int(loc % game.width))
    game.going(pos)
    # 玩家下一步棋结束

    # 电脑下一步棋开始
    game.calculator()
    # 电脑下一步棋结束
    return redirect(request.referrer)


if __name__ == '__main__':
    game = Calc()
    app.run(debug=True)
