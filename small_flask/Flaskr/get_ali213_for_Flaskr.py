# -*- coding: utf-8 -*-

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from pyquery import PyQuery as pq
import time
import random
import html
from flask.ext.sqlalchemy import SQLAlchemy
import os

import requests
import re
import json
import logging

logging.basicConfig(level=logging.INFO)
key_tuple = ("title", "keywords", "description", "game_name", "game_id", "source_url", "author", "doc_title", "content")

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

game_target = [
    ["变形金刚：毁灭", "http://gl.ali213.net/html/2015-10/86933", 30165],
]

init_dict = {}

par = re.compile(r'> +')
par_more = (
    re.compile(r'<p>更多相关资讯.+'),
    re.compile(r'<p></p>'),
    re.compile(r'<p>游戏专题[^<]+'),
    re.compile(r'<p>[^>]+213[^<]+</p>'))
par_need_del = ("\n", "\r", "　", "&#13;", "【游侠攻略组】")
par_in_title = (
    "_变形金刚：毁灭图文攻略详解",
    "_变形金刚：毁灭攻略秘籍_游侠网",
    "全关卡流程 + 全剧情 + 全收集",
    "全关卡流程+全剧情+全收集",
)


def init_db():
    db.create_all()


def html_format(unformed_str):
    temp = unformed_str.replace("\\", "\\\\")
    for item in par_need_del:
        temp = temp.replace(item, "")
    temp = re.sub(par, '>', temp)
    return temp.replace(r'"', r'\"').strip()


def get_content(this_target_url):
    this_target = requests.get(this_target_url).content.decode("utf-8")

    # 页面描述信息
    title = pq(pq(this_target)("title")).text()
    for item_p in par_in_title:
        title = title.replace(item_p, "")

    # 页面内容
    content_html = pq(pq(this_target)("div"))(".glzjshow_con")
    text = pq(content_html).html()
    for par_item in par_more:
        text = re.sub(par_item, '', text)
    abstract = pq(text).text()[:100] + "..."
    try:
        thumb = pq(pq(text)("img")[0]).attr("src")
    except:
        print("没有图")
        thumb = ""
    text = html.escape(text, quote=True)
    c_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    page_view = int(random.uniform(100, 5000))
    new_doc = Docs([title, text, abstract, c_time, "", page_view, "", "", thumb])

    logging.debug(thumb)
    logging.debug("\n\n")

    db.session.add(new_doc)
    db.session.commit()


if __name__ == '__main__':
    for game in game_target:
        init_dict["url_head"] = game[1]
        page_number = 1

        while 1:
            target_url = init_dict["url_head"] + "_" + str(page_number) + ".html"
            if page_number == 1:
                target_url = init_dict["url_head"] + ".html"
                print(target_url)
            time.sleep(0.4)

            try:
                get_content(target_url)
                page_number += 1
            except Exception as e:
                logging.info(str(e))
                break