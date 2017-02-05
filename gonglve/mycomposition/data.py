#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from functools import wraps
import time
import sys
import logging
logging.basicConfig(level=logging.INFO)


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    # SECRET_KEY="TEMP",
    # USERNAME="admin",
    # PASSWORD="admin",
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, "composition.db"),
    SQLALCHEMY_TRACK_MODIFICATIONS=True,
    POST_IN_SINGLE_PAGE=10,
)

db = SQLAlchemy(app)


class Docs(db.Model):
    doc_id = db.Column(db.Integer, primary_key=True)
    doc_md = db.Column(db.String)
    title = db.Column(db.String)
    content = db.Column(db.String)
    grade = db.Column(db.Integer)
    genre = db.Column(db.Integer)
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
    status = db.Column(db.Boolean)

    def __init__(self, init_list):
        self.doc_md = init_list[0]
        self.title = init_list[1]
        self.content = init_list[2]
        self.grade = init_list[3]
        self.genre = init_list[4]
        self.words = init_list[5]
        self.tags = init_list[6]
        self.author = init_list[7]
        self.view = init_list[8]
        self.yesterday_view = init_list[9]
        self.today_view = init_list[10]
        self.create_time = init_list[11]
        self.update_time = init_list[12]
        self.former_url = init_list[13]
        self.former_org = init_list[14]
        self.status = True

    def __repr__(self):
        return "<Docs %r" % self.doc_md

    def to_dict(self):
        return dict(
            doc_id=self.doc_id,
            doc_md=self.doc_md,
            title=self.title,
            content=self.content,
            grade=self.grade,
            genre=self.genre,
            words=self.words,
            tags=self.tags,
            author=self.author,
            view=self.view,
            yesterday_view=self.yesterday_view,
            today_view=self.today_view,
            create_time=self.create_time,
            update_time=self.update_time,
            former_url=self.former_url,
            former_org=self.former_org
        )


class Sugs(db.Model):
    title = db.Column(db.String, primary_key=True)
    same_docs = db.Column(db.String)
    similar_docs = db.Column(db.String)

    def __init__(self, c_list):
        self.title = c_list[0]
        self.same_docs = c_list[1]
        self.similar_docs = c_list[2]

    def get_same(self):
        if self.same_docs:
            return [int(item) for item in self.same_docs.split(",")]
        else:
            return []

    def get_similar(self):
        if self.similar_docs:
            return [int(item) for item in self.similar_docs.split(",")]
        else:
            return []


class Keywords(db.Model):
    key = db.Column(db.String, primary_key=True)
    weight = db.Column(db.Float)
    docs = db.Column(db.String)

    def __init__(self, c_list):
        self.key = c_list[0]
        self.weight = c_list[1]
        self.docs = c_list[2]

    def __repr__(self):
        return "<Keywords %r" % self.docs

    def get_docs(self):
        return set(map(int, self.docs.split(",")))


class Weights(db.Model):
    doc_id = db.Column(db.Integer, primary_key=True)
    title_weight = db.Column(db.Float)
    content_weight = db.Column(db.Float)

    def __init__(self, c_list):
        self.doc_id = c_list[0]
        self.title_weight = c_list[1]
        self.content_weight = c_list[2]


class Genre(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    docs = db.Column(db.String)

    def __init__(self, c_list):
        self.key, self.docs = c_list

    def __repr__(self):
        return "<Genre %r" % self.docs

    def get_docs(self):
        return set([int(item) for item in self.docs.split(",")])


class Grade(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    docs = db.Column(db.String)

    def __init__(self, c_list):
        self.key, self.docs = c_list

    def __repr__(self):
        return "<Grade %r" % self.docs

    def get_docs(self):
        return set([int(item) for item in self.docs.split(",")])


def cost_count(func):
    @wraps(func)
    def costing(*args, **kw):
        a = time.time()
        ret = func(*args, **kw)
        time_cost = int((time.time()-a) * 1000)
        if time_cost > 100:
            logging.warning("Func(" + str(func.__name__) + ")\tcost: " + str(time_cost) + " ms")
        return ret
    return costing


class ProgressBar:
    def __init__(self, count=0, total=0, width=50):
        self.count = count
        self.total = total
        self.width = width

    def move(self):
        self.count += 1
        sys.stdout.write(' ' * (self.width + 9) + '\r')
        sys.stdout.flush()
        progress = int(self.width * self.count / self.total)
        sys.stdout.write('{0:3}/{1:3}: '.format(self.count, self.total))
        sys.stdout.write('+' * progress + '-' * (self.width - progress) + '\r')
        if progress == self.width:
            sys.stdout.write('\n')
        sys.stdout.flush()
