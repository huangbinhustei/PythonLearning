# -*- coding: utf-8 -*-

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from pyquery import PyQuery as pq
import markdown2
import time
import random
import html
from flask.ext.sqlalchemy import SQLAlchemy
import os
from sqlalchemy import desc

path = os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/static/"
pic_list = []
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config.update(
    DEBUG=True,
    SECRET_KEY="TEMP",
    USERNAME="admin",
    PASSWORD="admin",
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, "flaskr.db"),
    SQLALCHEMY_TRACK_MODIFICATIONS=True,
    POST_IN_SINGL_PAGE=10,
)
db = SQLAlchemy(app)


class Docs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    text = db.Column(db.String)
    abstract = db.Column(db.String)
    c_time = db.Column(db.String)
    renew_time = db.Column(db.String)
    page_view = db.Column(db.Integer)
    tag = db.Column(db.String)
    category = db.Column(db.String)
    thumb = db.Column(db.String)

    def __init__(self, c_list):
        self.title = c_list[0]
        self.text = c_list[1]
        self.abstract = c_list[2]
        self.c_time = c_list[3]
        self.renew_time = c_list[4]
        self.page_view = c_list[5]
        self.tag = c_list[6]
        self.category = c_list[7]
        self.thumb = c_list[8]

    def __repr__(self):
        return "<Docs %r" % self.title

    def to_dict(self, isSafe):
        return dict(
            title=self.title,
            text=html.unescape(self.text) if isSafe else self.text,
            abstract=self.abstract,
            c_time=self.c_time,
            renew_time=self.renew_time,
            page_view=self.page_view,
            tag=self.tag,
            category=self.category,
            thumb=self.thumb,
        )


def get_categories_and_tags():
    categories = []
    tags = []
    for row in Docs.query.all():
        categories.append(str(row.category))
        tags.append(str(row.tag))
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
    for item in Docs.query.filter_by(category=entry["category"]).order_by(Docs.id):
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
            flash("登录！")
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


# @app.errorhandler(404)
# def page_not_found(error):
#     return redirect(url_for("show_entries"))


@app.route("/pic/<dir_name>")
def show_pic(dir_name="img"):
    print(path + pic_list[0][0] + "/" + pic_list[0][1][1])
    return "<img src=\"/static/" + pic_list[0][0] + "/" + pic_list[0][1][1] + "\">"


@app.before_first_request
def before_first_time():
    print("before_first_time？\n\n")
    for pic_dir in list(os.walk(path))[1:]:
        pic_list.append([pic_dir[0].replace(path, ""), pic_dir[2]])
    print(pic_list)


@app.before_request
def before_every_time():
    print(request.headers["User-Agent"])


# @app.after_request
# def after_every_time():
#     print("after_every_time")


if __name__ == '__main__':
    app.run(host='0.0.0.0')
