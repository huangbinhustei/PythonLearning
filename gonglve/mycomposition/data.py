#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config.update(
    DEBUG=True,
    SECRET_KEY="TEMP",
    USERNAME="admin",
    PASSWORD="admin",
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, "composition.db"),
    SQLALCHEMY_TRACK_MODIFICATIONS=True,
    POST_IN_SINGL_PAGE=10,
)
db = SQLAlchemy(app)


class Docs(db.Model):
    doc_id = db.Column(db.Integer, primary_key=True)
    doc_md = db.Column(db.String)
    title = db.Column(db.String)
    content = db.Column(db.String)
    grade = db.Column(db.String)
    genre = db.Column(db.String)
    words = db.Column(db.Integer)
    tags = db.Column(db.String)
    author = db.Column(db.String)
    view = db.Column(db.Integer)
    yesterday_view = db.Column(db.Integer)
    today_view = db.Column(db.Integer)
    create_time = db.Column(db.Integer)
    update_time = db.Column(db.Integer)
    former_url = db.Column(db.String)
    former_org = db.Column(db.String)

    def __init__(self, init_list):
        self.doc_md = init_list[0]
        self.title = init_list[1]
        self.content = init_list[2]
        self.grade = init_list[3]
        self.genre = init_list[4]
        self.words = int(init_list[5][:-1])
        self.tags = init_list[6]
        self.author = init_list[7]
        self.view = init_list[8]
        self.yesterday_view = init_list[9]
        self.today_view = init_list[10]
        self.create_time = init_list[11]
        self.update_time = init_list[12]
        self.former_url = init_list[13]
        self.former_org = init_list[14]

    def __repr__(self):
        return "<Docs %r" % self.doc_md


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String)
    doc_with_tag = db.Column(db.String)
    create_time = db.Column(db.Integer)
    update_time = db.Column(db.Integer)

    def __init__(self, c_list):
        self.tag = c_list[0]
        self.doc_with_tag = c_list[1]
        self.create_time = c_list[2]
        self.update_time = c_list[3]

    def __repr__(self):
        return "<Docs %r" % self.tag

    def get_docs(self):
        return self.doc_with_tag.split("\t")


class Sugs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    doc_by_sug = db.Column(db.String)
    create_time = db.Column(db.Integer)
    update_time = db.Column(db.Integer)

    def __init__(self, c_list):
        self.title = c_list[0]
        self.doc_by_sug = c_list[1]
        self.create_time = c_list[2]
        self.update_time = c_list[3]

    def __repr__(self):
        return "<Docs %r" % self.tag

    def get_docs(self):
        return self.doc_by_sug.split("\t")
