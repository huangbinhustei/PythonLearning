# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

path = os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/变形金刚：毁灭.txt"
data = {}
with open(path, "r") as f:
    data = json.loads(f.read())


@app.route("/", methods=["GET", "POST"])
@app.route("/<int:page_number_in_url>", methods=["GET", "POST"])
def home(page_number_in_url):
    name_d = request.args.get("type", "content")
    page_number = request.args.get("page_number", page_number_in_url)
    print(name_d)
    try:
        print(type(data[str(page_number)]))
        h = "<h1>" + data[str(page_number)]["title"] + "</h1><br>" + data[str(page_number)][name_d]
        return h
    except:
        return "<h1>没有这一页啊</h1>"


@app.route("/json/<int:page_number>", methods=["GET", "POST"])
@app.route("/json/<int:page_number>/<string:name_d>", methods=["GET", "POST"])
def json(page_number=1, name_d=""):
    try:
        if name_d == "":
            return jsonify(**data[str(page_number)])
        return data[str(page_number)][name_d]
    except:
        return "<h2>没有这一页啊</h2><br><h2>也可能是没有这个key啊</h2>"


@app.route("/post", methods=["GET", "POST"])
def for_post():
    if request.method == "GET":
        return "GET"
    if request.method == "POST":
        print("page is " + request.form["page_number"])
        print("he need " + request.form["type"])
        return data[request.form["page_number"]][request.form["type"]]


if __name__ == "__main__":
    app.run(host="192.168.1.101", debug=True)
