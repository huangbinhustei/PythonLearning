#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config.change(
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, "offer.db"),
    SQLALCHEMY_TRACK_MODIFICATIONS=True,
)
db = SQLAlchemy(app)


def get_value(d, k):
    if k not in d:
        return ""
    if isinstance(d[k], list):
        return "|".join(d[k])
    return d[k]


class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String)
    query = db.Column(db.String)
    job_name = db.Column(db.String)
    full_time = db.Column(db.String)
    age = db.Column(db.String)
    sex = db.Column(db.String)
    desc = db.Column(db.String)
    area = db.Column(db.String)
    experience = db.Column(db.String)
    industry = db.Column(db.String)
    education = db.Column(db.String)
    job_class = db.Column(db.String)
    salary = db.Column(db.String)
    welfare = db.Column(db.String)
    employer = db.Column(db.String)
    employer_type = db.Column(db.String)
    employer_size = db.Column(db.String)
    lastmod = db.Column(db.String)

    def __init__(self, arg, _data):
        self.city = _data["city"]
        self.query = _data["query"]
        self.job_name = get_value(arg, "name")
        self.full_time = get_value(arg, "@type")
        self.age = get_value(arg, "age")
        self.sex = get_value(arg, "sex")
        self.desc = get_value(arg, "description")
        self.area = get_value(arg, "area")
        self.experience = get_value(arg, "experience")
        self.industry = get_value(arg, "industry")
        self.education = get_value(arg, "education")
        self.job_class = "|".join([get_value(arg, "jobfirstclass"),
                                   get_value(arg, "jobsecondclass"),
                                   get_value(arg, "jobthirdclass"),
                                   get_value(arg, "jobfourthclass")])
        self.salary = get_value(arg, "salary")
        self.welfare = get_value(arg, "welfare")
        self.employer = get_value(arg, "officialname")
        self.employer_type = get_value(arg, "employertype")
        self.employer_size = get_value(arg, "ori_size")
        self.lastmod = get_value(arg, "lastmod")
