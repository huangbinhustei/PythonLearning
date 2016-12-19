#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from data import Docs, db, app
from flask import Flask, request, sessions, g, redirect, render_template, url_for, jsonify
from sqlalchemy import desc, and_
import time
import logging
from collections import defaultdict
import re

logging.basicConfig(level=logging.INFO)
par = re.compile("\.[a-z0-9A-Z]+{display: none;} 精彩内容，尽在百度攻略：http://gl.baidu.com")


@app.route("/view/<page_md>", methods=['GET'])
def page_view(page_md):
    a = time.time()
    doc = Docs.query.filter(Docs.doc_md == page_md).first()
    print(time.time() - a)
    if not doc:
        return jsonify({"error": "no such md"})

    entry = doc.to_dict()
    
    entry["content"] = []
    for item in re.sub(par, "\t", doc.content).split("\t"):
        for s in item.split(" "):
            entry["content"].append(s)
    doc.view += 1
    db.session.commit()
    return render_template("view.html",entry=entry)
    

@app.route("/api/view/<page_md>", methods=['GET'])
def api_view(page_md):
    a = time.time()
    doc = Docs.query.filter(Docs.doc_md == page_md).first()
    print(time.time() - a)
    if not doc:
        return jsonify({"error": "no such md"})
    target = request.args.get('target')
    if target:
        return jsonify({target:doc.to_dict()[target]})
    return jsonify(**doc.to_dict())


@app.route("/api/list", methods=['GET'])
def api_list():
    a = time.time()
    grade = request.args.get('grade')
    genre = request.args.get('genre')
    words = request.args.get('words')

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
    print(time.time() - a)
    return jsonify(**lists)


if __name__ == '__main__':
    app.run(debug=True)
