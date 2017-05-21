#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Flask, render_template, request, redirect, url_for
from gomoku import Calc, Game, Danger

app = Flask(__name__)

B = 1
W = 2
a = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 2, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]


@app.route("/")
def home():
    loc = request.args.get('loc')
    restart = request.args.get('restart')
    if restart:
        game.restart()
        fir = request.args.get('aifirst')
        if fir == "1":
            game.going((5, 5))
        return redirect(url_for("home"))
    if not loc:
        return render_template("home.html", game=game)
    # 玩家下一步棋开始
    loc = int(loc)
    pos = (int(loc / game.width), int(loc % game.width))
    game.going(pos)
    # 玩家下一步棋结束

    # 电脑下一步棋开始
    player = B if (game.step + 1) % 2 == 1 else W
    d = Danger(game.grid, player)
    pos = d.calc()

    if pos:
        game.going(pos)
    else:
        pos = game.calculator()
        game.going(pos)
    # 电脑下一步棋结束
    return redirect(request.referrer)


if __name__ == '__main__':
    game = Calc()
    # game = Game()
    app.run(host="0.0.0.0", debug=True)
