# -*- coding: utf-8 -*-

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from pyquery import PyQuery as pq
import markdown2
import time
import random
import html
from flask.ext.sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config.update(
    DATABASE="flaskr.db",
    DEBUG=True,
    SECRET_KEY="TEMP",
    USERNAME="admin",
    PASSWORD="admin",
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, "flaskr.db"),
    SQLALCHEMY_TRACK_MODIFICATIONS=True,
    POST_IN_SINGL_PAGE=3
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


def init_db():
    db.create_all()


@app.route("/")
@app.route("/<int:page_id>")
def show_entries(page_id=1):
    paginate = Docs.query.paginate(page_id, app.config["POST_IN_SINGL_PAGE"], False)
    posts = paginate.items
    entries = []
    titles = []
    for row in posts:
        temp_thumb = row.thumb
        if "" == temp_thumb:
            temp_thumb = "http://192.168.1.101/%E5%A3%81%E7%BA%B8/01991_autumnlake_1600x1200.jpg"
        entry = row.__dict__
        entry["thumb"] = temp_thumb
        entries.append(entry)

        temp_title = str(row.title)
        if len(temp_title) > 12:
            temp_title = str(entry["title"])[:12] + "..."
        temp = row.__dict__
        temp["title"] = temp_title
        titles.append(temp)

    return render_template("show_entries.html", entries=entries, titles=titles, paginate=paginate)


@app.route("/view/<int:doc_id>")
def view(doc_id):
    this_post = Docs.query.get_or_404(doc_id)
    entry = this_post.__dict__
    entry["text"] = html.unescape(this_post.text)
    titles = []
    for item in Docs.query.limit(10).all():
        titles.append([item.__dict__["id"], item.__dict__["title"]])
    return render_template("view.html", entry=entry, titles=titles)


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
        flash("done")
        return redirect(url_for("show_entries"))
    else:
        return render_template("add.html")


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
            flash("U R IN")
            return redirect(url_for("show_entries"))
    return render_template("login.html", error=error)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop('logged_in', None)
    return redirect(url_for("show_entries"))


@app.route("/home", methods=["GET"])
def home():
    if request.method == "GET":
        return render_template("home.html")
    else:
        print("haha")
        return render_template("home.html")


@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for("show_entries"))


if __name__ == '__main__':

    app.run()
