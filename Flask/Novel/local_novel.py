# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from flask import render_template
import sqlite3
import json
import time

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
@app.route("/<int:id>", methods=["GET", "POST"])
def home(id=1):
    ch_id = id
    connect = sqlite3.connect("novel.db")
    cursor = connect.cursor()
    sql_sentence = "select title,content from the_door where key_chapter == " + str(ch_id)
    cursor.execute(sql_sentence)
    values_temp = cursor.fetchall()
    if not values_temp:
        input("sth wrong \n")
    tit = str(values_temp[0][0])
    tit = tit.replace(" - 88小说网", "")
    tit = tit.replace("造化之门 - ", "")
    txt = values_temp[0][1]
    fw = txt.split(" ")
    fw = fw[1:-11]
    # print(fw)
    preview_url = "http://192.168.1.101:5000/" + str(ch_id - 1)
    next_url = "http://192.168.1.101:5000/" + str(ch_id + 1)
    return render_template("home.html", biao_ti=tit, nei_rong=fw, p_url=preview_url, n_url=next_url)


if __name__ == "__main__":
    app.run(host="192.168.1.101", debug=True)
