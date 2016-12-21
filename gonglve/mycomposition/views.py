#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from data import Docs, db, app
from flask import request, sessions, g, redirect, render_template, url_for, jsonify
from sqlalchemy import desc, and_
import time
import logging
from collections import defaultdict
import re
from datetime import datetime
from functools import wraps

logging.basicConfig(level=logging.INFO)
par = re.compile("\.[a-z0-9A-Z]+\{display: none;} 精彩内容，尽在百度攻略：http://gl\.baidu\.com")


def cost_count(func):
    @wraps(func)
    def wraper(*args, **kw):
        a = time.time()
        ret = func(*args, **kw)
        print(time.time()-a)
        return ret
    return wraper


def view_counts(t_doc):
    t_doc.view += 1
    today = int(time.time()/86400)
    if t_doc.update_time == today:
        t_doc.today_view += 1
    elif t_doc.update_time + 1 == today:
        t_doc.update_time = today
        t_doc.today_view = 1
        t_doc.yesterday_view = t_doc.today_view
    else:
        t_doc.update_time = today
        t_doc.today_view = 1
    db.session.commit()


@app.route("/view/<page_md>", methods=['GET'])
@cost_count
def page_view(page_md):
    doc = Docs.query.filter(Docs.doc_md == page_md).first()
    if not doc:
        return jsonify({"error": "no such md"})

    entry = doc.to_dict()
    entry["content"] = []
    for item in re.sub(par, "\t", doc.content).split("\t"):
        for s in item.split(" "):
            entry["content"].append(s)
    view_counts(doc)
    return render_template("view.html", entry=entry)
    

@app.route("/api/view/<page_md>", methods=['GET'])
@cost_count
def api_view(page_md):
    doc = Docs.query.filter(Docs.doc_md == page_md).first()
    if not doc:
        return jsonify({"error": "no such md"})
    target = request.args.get('target')
    if target:
        return jsonify({target: doc.to_dict()[target]})
    return jsonify(**doc.to_dict())


@app.route("/api/list", methods=['GET'])
@cost_count
def api_list():
    grade, genre, words = (request.args.get('grade'), request.args.get('genre'), request.args.get('words'))
    query = Docs.query
    if grade:
        query = query.filter(Docs.grade == grade)
    if genre:
        query = query.filter(Docs.genre == genre)
    if words:
        query = query.filter(Docs.words >= words)
    lists = defaultdict(lambda: 0)
    for item in query.paginate(0, 20, False).items:
        lists[item.doc_md] = item.to_dict()
    return jsonify(**lists)


@app.before_request
def before_request():
    this_url = str(request.url).replace("http://127.0.0.1:5000/", "")
    logging.info(str(datetime.now()) + "\t" + this_url)


if __name__ == '__main__':
    app.run(debug=True)
