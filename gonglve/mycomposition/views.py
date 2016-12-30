#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from data import Docs, db, app, cost_count
from my_search import search_by_title
from flask import request, sessions, g, redirect, render_template, url_for, jsonify
from sqlalchemy import desc
import logging
from collections import defaultdict, OrderedDict
import json
import os
import time

logging.basicConfig(level=logging.INFO)
basedir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(basedir, "config.json"), "r", encoding="utf-8") as f:
    map_dict = json.loads(f.read())
    genre_map = OrderedDict(sorted(map_dict["genre_map"].items(), key=lambda t: int(t[0])))
    grade_map = OrderedDict(sorted(map_dict["grade_map"].items(), key=lambda t: int(t[0])))


@app.route("/")
@cost_count
def page_list():
    try:
        page_id = int(request.args.get("page"))
    except:
        logging.error("Page ID Is Not Integer")
        page_id = 0
    grade, genre, words = (request.args.get('grade'), request.args.get('genre'), request.args.get('words'))
    query = Docs.query
    if grade:
        query = query.filter(Docs.grade == grade)
    if genre:
        query = query.filter(Docs.genre == genre)
    if words:
        query = query.filter(Docs.words >= words)
    paginate = query.paginate(page_id, app.config["POST_IN_SINGLE_PAGE"], False)

    entries = []
    for entry in paginate.items:
        entries.append(dict(
            title=entry.title,
            grade=map_dict["grade_map"][str(entry.grade)],
            genre=map_dict["genre_map"][str(entry.genre)],
            author="佚名" if entry.author == "" else entry.author,
            # content=pq(entry.content).text()[:100],
            content=entry.content.replace("<p>","").replace("</p>","")[:100],
            view=entry.view,
            doc_md=entry.doc_md,
        ))

    titles = []
    for item in Docs.query.order_by(desc(Docs.view)).limit(10):
        titles.append(dict(
            title=item.title,
            view=item.view,
            doc_md=item.doc_md,
        ))

    return render_template("page_list.html",
                           entries=entries,
                           titles=titles,
                           paginate=paginate,
                           genre_map=genre_map,
                           grade_map=grade_map,
                           )


@app.route("/view/<page_md>", methods=['GET'])
@cost_count
def page_view(page_md):
    doc = Docs.query.filter(Docs.doc_md == page_md).first()
    if not doc:
        return jsonify({"error": "no such md"})

    entry = doc.to_dict()
    entry["grade"] = map_dict["grade_map"][str(entry["grade"])]
    entry["genre"] = map_dict["genre_map"][str(entry["genre"])]
    entry["author"] = "佚名" if entry["author"] == "" else entry["author"]

    doc.view += 1
    today = int(time.time()/86400)
    if doc.update_time == today:
        doc.today_view += 1
    elif doc.update_time + 1 == today:
        doc.update_time = today
        doc.yesterday_view = doc.today_view
        doc.today_view = 1
    else:
        doc.update_time = today
        doc.today_view = 1
    db.session.commit()

    recommends = []
    for line in search_by_title(entry["title"])[:10]:
        doc_id, doc_value = line[0], str(line[1])
        sug_doc = Docs.query.get(doc_id)
        print("\t".join([sug_doc.title, doc_value]))
        recommends.append(sug_doc)

    return render_template("page_view.html",
                           entry=entry,
                           genre_map=genre_map,
                           grade_map=grade_map,
                           recommends=recommends,
                           )


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
    this_url = str(request.url).replace("http://127.0.0.1:5000", "")
    logging.info("request: " + this_url + " @ " + str(time.ctime()))


if __name__ == '__main__':
    app.run()
