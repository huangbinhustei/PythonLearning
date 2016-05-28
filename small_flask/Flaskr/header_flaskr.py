# -*- coding: utf-8 -*-

from flask import Flask
import html
from flask.ext.sqlalchemy import SQLAlchemy
import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/static/"
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

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


class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    game_desc = db.Column(db.String)
    cover = db.Column(db.String)
    doc_count = db.Column(db.Integer)
    game_type = db.Column(db.String)
    c_time = db.Column(db.String)
    renew_time = db.Column(db.String)

    def __init__(self, init_list):
        self.name = init_list[0]
        self.game_desc = init_list[1]
        self.cover = init_list[2]
        self.doc_count = init_list[3]
        self.game_type = init_list[4]
        self.c_time = init_list[5]
        self.renew_time = init_list[6]

    def __repr__(self):
        return "<Docs %r" % self.name


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String)
    doc_with_tag = db.Column(db.String)

    def __init__(self, c_list):
        self.tag = c_list[0]
        self.doc_with_tag = c_list[1]

    def __repr__(self):
        return "<Docs %r" % self.tag


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
