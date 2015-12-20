# -*- coding: utf-8 -*-

from flask import Flask
from flask import request
from flask import render_template
import sys
sys.path.append("..")
import recommending.sug as tui_jian

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")


@app.route("/", methods=["POST"])
def after_input():
    query = request.form["equation"]
    titles = []
    try:
        temp = tui_jian.me_main(query)
        for item in temp:
            x_temp = item.strip().split("\t")
            t = x_temp[0]
            w = str(round(float(x_temp[1]) * 100, 2))+"%"
            titles.append([t, w])
        return render_template("home.html", equation=query, ans_list=titles)
    except Exception as e:
        print(e)
        print("sth wrong")
        return render_template("home.html", equation="出错啦，啦啦啦", ans_list=[[]])


if __name__ == "__main__":
    app.run(host="192.168.1.107", debug=True)

