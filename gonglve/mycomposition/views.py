#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from data import Docs, db, app, cost_count, Titles
from my_search import search_by_title
from flask import request, sessions, g, redirect, render_template, url_for, jsonify
from sqlalchemy import desc
import logging
from collections import defaultdict, OrderedDict
import json
import os
import time
import random

logging.basicConfig(level=logging.ERROR)
basedir = os.path.abspath(os.path.dirname(__file__))
page_len = app.config["POST_IN_SINGLE_PAGE"]
with open(os.path.join(basedir, "config.json"), "r", encoding="utf-8") as f:
    map_dict = json.loads(f.read())
    genre_map = OrderedDict(sorted(map_dict["genre_map"].items(), key=lambda t: int(t[0])))
    grade_map = OrderedDict(sorted(map_dict["grade_map"].items(), key=lambda t: int(t[0])))


def get_idx(id_name):
    _str = request.args.get(id_name)
    if _str is None:
        return []
    if "," in _str:
        idx = [int(item) for item in _str.split(",")]
    else:
        try:
            idx = [int(_str)]
        except ValueError:
            logging.debug(id_name + " ID Is Not Integer")
            idx = []
    return idx


def get_paginate(this_list):
    page_id = get_page_id()
    page_max = int((len(this_list) + 1) / page_len) - 1
    this_list = this_list[page_id * page_len:(page_id + 1) * page_len]
    if page_id > page_max:
        logging.info("页码过大")
    if page_id < 0:
        logging.info("页码过小")
    paginate = dict(
        has_prev=False if page_id == 0 else True,
        has_next=False if page_id >= page_max else True,
        page=page_id,
        prev_num=max(0, page_id - 1),
        next_num=min(page_id + 1, page_max))
    return this_list, paginate


def get_page_id():
    try:
        page_id = int(request.args.get("page"))
    except TypeError:
        logging.debug("Page ID Is Empty")
        page_id = 0
    except ValueError:
        logging.debug("Page ID Is Not Integer")
        page_id = 0

    return page_id


def time_format(a):
    return time.ctime(a)


@app.route("/")
@cost_count
def page_list():
    def page_normal_list():
        query = Docs.query
        if grade:
            query = query.filter(Docs.grade == grade)
        if genre:
            query = query.filter(Docs.genre == genre)
        if words:
            query = query.filter(Docs.words >= words)
        return query.paginate(page_id, app.config["POST_IN_SINGLE_PAGE"], False)

    def page_titles():
        query = Docs.query
        same_titles = Titles.query.get(title)
        if not same_titles:
            query = query.filter(Docs.title == title)
            return query.paginate(page_id, app.config["POST_IN_SINGLE_PAGE"], False)
        else:
            same_titles = same_titles.docs.split(",")
            query = query.filter(Docs.doc_id.in_(same_titles))
            return query.paginate(page_id, app.config["POST_IN_SINGLE_PAGE"], False)

    page_id = get_page_id()
    grade, genre, words = (request.args.get('grade'), request.args.get('genre'), request.args.get('words'))
    title = request.args.get("title")

    if title:
        paginate = page_titles()
        query_prefix = "title=" + title
    else:
        paginate = page_normal_list()
        query_prefix = ""

    entries = []
    for entry in paginate.items:
        temp = entry.to_dict()
        temp["author"] = entry.author
        temp["content"] = entry.content
        entries.append(temp)

    hottest_titles = Docs.query.order_by(desc(Docs.view)).limit(20)

    return render_template("page_list.html",
                           entries=entries,
                           titles=hottest_titles,
                           query_prefix=query_prefix,
                           paginate=paginate,
                           genre_map=genre_map,
                           grade_map=grade_map,
                           )


@app.route("/search", methods=['GET'])
@cost_count
def page_search():
    washer = defaultdict(int)
    query = request.args.get('query')
    grade = get_idx("grade")
    genre = get_idx("genre")

    if not query:
        return "<h2>搜索起始页</h2>"

    if -1 not in grade or -1 not in genre:
        washer["filter"] = True
        washer["grade"] = grade
        washer["genre"] = genre
    result_search, paginate = get_paginate(search_by_title(query, washer=washer))

    return render_template("page_search.html",
                           res=result_search,
                           paginate=paginate,
                           query=query,
                           genre_map=genre_map,
                           grade_map=grade_map,
                           )


@app.route("/view/<page_md>", methods=['GET'])
@cost_count
def page_view(page_md):
    def view_update():
        doc.view += 1
        today = int(time.time() / 86400)
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

    doc = Docs.query.filter(Docs.doc_md == page_md).first()
    if not doc:
        return jsonify({"error": "no such md"})

    entry = doc.to_dict()

    view_update()

    titles = Titles.query.get(doc.title)
    same_titles = []
    if titles:
        title_ids = Titles.query.get(doc.title).docs.split(",")
        if str(doc.doc_id) in title_ids:
            ind = title_ids.index(str(doc.doc_id))
        else:
            ind = 0
            logging.error(doc.doc_md + ":doc title changes without updating Titles")
        group_id = int(ind / 10)
        group_offset = ind % 10
        titles = Docs.query.filter(Docs.doc_id.in_(title_ids[group_id * 10:(group_id + 1) * 10]))
        if ind == 0:
            doc_prev = ""
            doc_next = Docs.query.get(title_ids[1])
        elif ind == len(title_ids) - 1:
            doc_prev = Docs.query.get(title_ids[ind - 1])
            doc_next = ""
        else:
            doc_prev = Docs.query.get(title_ids[ind - 1])
            doc_next = Docs.query.get(title_ids[ind + 1])

        same_titles = [titles, group_offset, group_id, doc_prev, doc_next]

    recommends = [Docs.query.get(line[0]) for line in search_by_title(entry["title"], topx=15)]
    if doc in recommends:
        recommends.remove(doc)
    page_next = random.choice(recommends)
    recommends.remove(page_next)

    return render_template("page_view.html",
                           entry=entry,
                           genre_map=genre_map,
                           grade_map=grade_map,
                           titles=titles,
                           recommends=recommends,
                           page_next=page_next,
                           same_titles=same_titles,
                           )


@app.route("/edit/<page_md>", methods=['GET', 'POST'])
@app.route("/dashboard/edit/<page_md>", methods=['GET', 'POST'])
@cost_count
def dashboard_edit(page_md):
    entry = Docs.query.filter(Docs.doc_md == page_md).first()
    if not entry:
        return jsonify({"error": "no such md"})
    if request.method == "GET":
        return render_template("dashboard_edit.html",
                               entry=entry,
                               genre_map=genre_map,
                               grade_map=grade_map,
                               )
    else:
        entry.title = request.form["title"]
        entry.grade = int(request.form["grade"])
        entry.genre = int(request.form["genre"])
        entry.author = request.form["author"]
        entry.content = request.form["content"]
        db.session.commit()
        return redirect(url_for("page_view", page_md=page_md))


@app.route("/dashboard/list", methods=["GET", "POST"])
@cost_count
def dashboard_doc_list():

    def get_by_id(idx):
        pass

    query = Docs.query
    options = [-1, -1]  # 年级、体裁筛选的默认选项
    page_id = get_page_id()
    if request.method == "GET":
        title = request.args.get("title")
        title = "" if title is None else title
        doc_md = ""
    else:
        doc_md = request.form["doc_md"]
        title = request.form["title"]
    grade = get_idx("grade")
    genre = get_idx("genre")

    entries = []
    if doc_md:
        print("if doc_md")
        entries.append(query.filter(Docs.doc_md == doc_md).first())
        entries, paginate = get_paginate(entries)
    elif title:
        print("if title")
        for line in search_by_title(title, need_same=True):
            doc_id, doc_value = line[0], str(line[1])
            entries.append(Docs.query.get(int(doc_id)))
        entries, paginate = get_paginate(entries)
    else:
        print("else")
        if grade != -1:
            query = query.filter(Docs.grade == grade)
        if genre != -1:
            query = query.filter(Docs.genre == genre)
        options = [grade, genre]
        paginate = query.paginate(page_id, app.config["POST_IN_SINGLE_PAGE"], False)
        entries = paginate.items

    return render_template("dashboard_list.html",
                           entries=entries,
                           paginate=paginate,
                           options=options,
                           genre_map=genre_map,
                           grade_map=grade_map,
                           query=title,
                           )


@app.route("/dashboard", methods=["GET"])
@cost_count
def dashboard():
    return render_template("dashboard.html",
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
