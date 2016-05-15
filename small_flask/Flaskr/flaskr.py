# -*- coding: utf-8 -*-

from header_flaskr import Docs, Tags, db, app
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from pyquery import PyQuery as pq
import markdown2
import html
import random
from sqlalchemy import desc
import time
import logging
logging.basicConfig(level=logging.INFO)


def get_categories_and_tags():
    categories = []
    tags = []
    for row in Docs.query.all():
        categories.append(str(row.category))
    for row in Tags.query.all():
        tags.append(row.tag)
    return [list(set(categories)), list(set(tags))]


@app.route("/")
@app.route("/<int:page_id>")
def show_entries(page_id=1):
    paginate = Docs.query.paginate(page_id, app.config["POST_IN_SINGL_PAGE"], False)
    posts = paginate.items

    entries = []
    for row in posts:
        temp_thumb = row.thumb
        if "" == temp_thumb:
            temp_thumb = "http://192.168.1.101/%E5%A3%81%E7%BA%B8/01991_autumnlake_1600x1200.jpg"
        entry = row.__dict__
        entry["thumb"] = temp_thumb
        entries.append(entry)

    titles = []
    for item in Docs.query.order_by(desc(Docs.page_view)).limit(10):
        temp = item.__dict__
        titles.append(temp)

    return render_template("show_entries.html",
                           entries=entries,
                           titles=titles,
                           paginate=paginate,
                           categories=get_categories_and_tags()[0],
                           tags=get_categories_and_tags()[1]
                           )


@app.route("/view/<int:doc_id>")
def view(doc_id):
    this_post = Docs.query.get_or_404(doc_id)
    entry = this_post.__dict__
    entry["text"] = html.unescape(this_post.text)
    titles = []
    for item in Docs.query.filter_by(category=entry["category"]).order_by(Docs.id).limit(15):
        titles.append(item.__dict__)
    return render_template("view.html",
                           entry=entry,
                           titles=titles,
                           categories=get_categories_and_tags()[0],
                           tags=get_categories_and_tags()[1])


@app.route("/add", methods=["GET", "POST"])
def add_entry():
    if not session.get("logged_in"):
        abort(401)
    if request.method == "POST":
        title = request.form["title"]
        text = markdown2.markdown(request.form["text"])
        abstract = pq(text).text()[:100] + "..."
        c_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        page_view = int(random.uniform(100, 5000))
        try:
            thumb = pq(pq(text)("img")[0]).attr("src")
        except:
            print("没有图")
            thumb = ""
        text = html.escape(text, quote=True)

        if not str(title).strip() or not str(request.form["text"]).strip():
            return render_template("add.html", error="请输入标题和正文")

        new_doc = Docs([title, text, abstract, c_time, "", page_view, "", "", thumb])
        db.session.add(new_doc)
        db.session.commit()
        flash("恭喜你又水了一贴")
        return redirect(url_for("show_entries"))
    else:
        return render_template("add.html",
                               categories=get_categories_and_tags()[0],
                               tags=get_categories_and_tags()[1])


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form["username"] != app.config["USERNAME"]:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session["logged_in"] = True
            flash("登录成功！")
            return redirect(url_for("show_entries"))
    return render_template("login.html", error=error,
                           categories=get_categories_and_tags()[0],
                           tags=get_categories_and_tags()[1])


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop('logged_in', None)
    return redirect(url_for("show_entries"))


@app.route("/json", methods=["GET", "POST"])
def api_json():
    if request.method == "POST":
        doc_id = request.form["DOC_ID"]
    else:
        doc_id = request.args.get("doc_id", "")
    this_post = Docs.query.get_or_404(doc_id)
    entry = this_post.to_dict(True)
    return jsonify(**entry)


@app.route("/json/<int:doc_id>", methods=["GET"])
@app.route("/json/<int:doc_id>/<name_d>", methods=["GET"])
def json(doc_id=1, name_d=""):
    this_post = Docs.query.get_or_404(doc_id)
    entry = this_post.to_dict(True)
    if name_d == "":
        return jsonify(**entry)
    else:
        single_dict = dict()
        single_dict[name_d] = entry[name_d]
    return jsonify(**single_dict)


@app.route("/category/<this_category>")
def category(this_category="haha"):
    titles = []
    for item in Docs.query.filter_by(category=this_category).order_by(Docs.id):
        titles.append(item.__dict__)

    return render_template("category.html",
                           game_name=this_category,
                           titles=titles,
                           categories=get_categories_and_tags()[0],
                           tags=get_categories_and_tags()[1])


@app.route("/tag/<this_tag>")
def tag(this_tag="haha"):
    titles = []
    titles2 = []
    a = time.time()
    for item in Docs.query.filter(Docs.tag.like("%" + this_tag + "%")).order_by(Docs.id):
        titles.append(item.__dict__)
    b = time.time()
    for item in Tags.query.filter_by(tag=this_tag):
        for doc_id in item.doc_with_tag.split(","):
            titles2.append(Docs.query.get(doc_id).__dict__)
    c = time.time()
    print(str(b-a) + "\t" + str(c-b))
    return render_template("category.html",
                           tag=this_tag,
                           titles=titles,
                           categories=get_categories_and_tags()[0],
                           tags=get_categories_and_tags()[1])


# @app.errorhandler(404)
# def page_not_found(error):
#     return redirect(url_for("show_entries"))


@app.before_first_request
def before_first_time():
    logging.debug("before_first_time？\n\n")


@app.before_request
def before_every_time():
    logging.debug(request.headers["User-Agent"])


# @app.after_request
# def after_every_time():
#     print("after_every_time")


if __name__ == '__main__':
    app.run()
