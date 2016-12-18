#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from data import Docs, db, app
from flask import Flask, request, sessions, g, redirect, render_template, url_for, jsonify
from sqlalchemy import desc, and_
import time
import logging

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
	query = Docs.query
	if grade:
		query = query.filter(Docs.grade==grade)
	if genre:
		query = query.filter(Docs.genre=genre)
	if words:
		query = query.filter(Docs.words>=words)
	query.paginate(0, 20, False)


	
    lists = Docs.query.paginate(0, 20, False)
    pars = dict(request.args.items())

    if request.args.get('grade'):
        if request.args.get("genre"):
            if request.args.get("words"):
                lists = Docs.query.filter(and_(
                    Docs.grade == request.args.get('grade'),
                    Docs.genre == request.args.get("genre"),
                    Docs.words >= request.args.get("words"))
                ).paginate(0, 20, False)
    # grade = pars["grade"] if "grade" in pars else ""
    # genre = pars["genre"] if "genre" in pars else ""
    # words = pars["words"] if "words" in pars else ""

    return jsonify(**lists[0])


if __name__ == '__main__':
    app.run(debug=True)
