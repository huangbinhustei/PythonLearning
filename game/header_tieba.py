# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config.update(
    DEBUG=True,
    # SECRET_KEY="TEMP",
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, "game_analysis.db"),
    SQLALCHEMY_TRACK_MODIFICATIONS=True,
)
db = SQLAlchemy(app)


class Tieba(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    name = db.Column(db.String)
    num_followers = db.Column(db.Integer)
    num_posts = db.Column(db.Integer)
    time = db.Column(db.String)

    def __init__(self, init_list):
        self.type = init_list[0]
        self.name = init_list[1]
        self.num_followers = init_list[2]
        self.num_posts = init_list[3]
        self.time = init_list[4]

    def __repr__(self):
        return "<Docs %r" % self.name
