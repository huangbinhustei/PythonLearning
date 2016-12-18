#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from data import Docs, db, app
from flask import Flask, request, sessions, g, redirect, render_template, url_for, jsonify
from sqlalchemy import desc, and_
import time
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO)


@app.route("/api/view/<page_md>", methods=['GET'])
def api_view(page_md, target=""):
    a = time.time()
    doc = Docs.query.filter(Docs.doc_md == page_md).first()
    print(time.time() - a)
    if not doc:
        return jsonify({"error": "no such md"})
    return jsonify(**doc.to_dict())


@app.route("/api/list", methods=['GET'])
def api_list():
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
    return jsonify(**lists)


if __name__ == '__main__':
    app.run(debug=True)
