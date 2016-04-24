# -*- coding: utf-8 -*-

import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
from pyquery import PyQuery as pq
import markdown2
import time
import random

app = Flask(__name__)

app.config.update(
    DATABASE="flaskr.db",
    DEBUG=True,
    SECRET_KEY="TEMP",
    USERNAME="admin",
    PASSWORD="admin"
)


def connect_db():
    return sqlite3.connect(app.config["DATABASE"])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource("schema.sql", "r") as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.after_request
def after_requests(response):
    g.db.close()
    return response


@app.route("/")
def show_entries():
    cur1 = g.db.execute("select title, abstract, id, c_time, page_view from entries order by id desc limit 6")
    entries = [dict(title=row[0], abstract=row[1], id=str(row[2]), c_time=row[3], page_view=row[4])
               for row in cur1.fetchall()]

    cur2 = g.db.execute("select title, id, c_time, page_view from entries order by page_view desc limit 10")
    titles = []
    for row in cur2.fetchall():
        temp_title = str(row[0])
        if len(temp_title) > 12:
            temp_title = str(row[0])[:12]+"..."
        titles.append(dict(title=temp_title, id=row[1], c_time=str(row[2]), page_view=row[3]))

    return render_template("show_entries.html", entries=entries, titles=titles)


@app.route("/view/<int:page_number>")
def view(page_number):
    sql = "select title, text, c_time, page_view from entries where id =" + str(page_number)
    cur = g.db.execute(sql)
    entries = [dict(title=row[0], text=row[1], c_time=row[2], page_view=row[3]) for row in cur.fetchall()]
    return render_template("view.html", entries=entries)


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/add", methods=["GET", "POST"])
def add_entry():
    if not session.get("logged_in"):
        abort(401)
    if request.method == "POST":
        title = request.form["title"]
        text = markdown2.markdown(request.form["text"])
        c_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        page_view = int(random.uniform(100, 5000))

        if not str(title).strip() or not str(request.form["text"]).strip():
            return render_template("add.html", error="请输入标题和正文")
        abstract = pq(text).text()[:80] + "..."
        sql = "insert into entries (title, text, abstract, c_time, page_view) values" \
              " (\"" + title + "\",\"" + text + "\",\"" + abstract + "\",\"" + c_time + "\",\"" + str(page_view) + "\")"
        g.db.execute(sql)
        g.db.commit()
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


@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for("show_entries"))


if __name__ == '__main__':
    # init_db()
    app.run()
