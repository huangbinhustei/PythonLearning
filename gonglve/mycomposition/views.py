#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from data import Docs, db, app
from flask import Flask, request, sessions, g, redirect, render_template, url_for, jsonify
from sqlalchemy import desc
import time
import logging
logging.basicConfig(level=logging.INFO)


@app.route("/api/view/<page_md>", methods=['GET'])
def api_view(page_md, target=""):

    a = time.time()
    doc = Docs.query.filter_by(doc_md=page_md).first()
    print(time.time()-a)
    if not doc:
        return jsonify({"error": "no such md"})
    return jsonify(**doc.to_dict())


@app.route("/api/list/<grade>/<genre>/<words>/<int:page_length>/<int:page_count>", methods=['GET'])
def api_list(grade="", genre="", words="", page_length=20, page_count=0):
    pass

if __name__ == '__main__':
    app.run(debug=True)