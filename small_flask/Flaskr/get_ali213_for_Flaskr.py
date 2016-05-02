# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from pyquery import PyQuery as pq
import time
import random
import html
import os

import requests
import re
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
    ["巫师3", "http://gl.ali213.net/html/2015-5/68823", 1766],
    ["辐射4", "http://gl.ali213.net/html/2015-11/91753", 10681],
    ["GTA5（侠盗猎车手5）", "http://gl.ali213.net/html/2015-4/65525", 11018],
    ["变形金刚：毁灭", "http://gl.ali213.net/html/2015-10/86933", 30165],
    # ["彩虹六号：围攻", "http://gl.ali213.net/html/2015-12/95215", 30166],
    # ["恶灵附身", "http://gl.ali213.net/html/2014-10/50191", 30167],
    # ["方舟：生存进化", "http://gl.ali213.net/html/2015-6/69805", 30168],
    # ["古墓丽影：崛起", "http://gl.ali213.net/html/2015-11/91031", 30169],
    # ["合金装备5：幻痛", "http://gl.ali213.net/html/2015-9/81963", 30170],
    # ["龙之信条：黑暗崛起", "http://gl.ali213.net/html/2016-1/102239", 30171],
    # ["三国志13", "http://gl.ali213.net/html/2016-1/105399", 30172],
    # ["生化危机0高清版", "http://gl.ali213.net/html/2016-1/104039", 30173],
    # ["使命召唤12：黑色行动3", "http://gl.ali213.net/html/2015-11/91245", 30174],
    # ["侠客风云传", "http://gl.ali213.net/html/2015-7/76033", 30175],
    # ["伊苏：树海", "http://gl.ali213.net/html/2015-10/89997", 30176],
    # ["勇者斗恶龙：英雄", "http://gl.ali213.net/html/2015-12/95807", 30177],
    # ["正当防卫3", "http://gl.ali213.net/html/2015-12/95217", 30178],
    # ["刺客信条：枭雄", "http://gl.ali213.net/html/2015-11/90629", 30179],
    # ["刺客信条4：黑旗", "http://gl.ali213.net/html/2014-6/42484", 30180],
    # ["刺客信条：大革命", "http://gl.ali213.net/html/2014-11/53997", 30181],
    # ["刺客信条：兄弟会", "http://gl.ali213.net/html/2014-6/42505", 30182],
    # ["刺客信条：叛变", "http://gl.ali213.net/html/2014-11/53675", 30183],
    # ["刺客信条：启示录", "http://gl.ali213.net/html/2014-6/42610", 30184],
    # ["火影忍者：究极忍者风暴4", "http://gl.ali213.net/html/2015-8/77655", 30185],
    # ["孤岛惊魂4", "http://gl.ali213.net/html/2014-11/54427", 30186],
    # ["消逝的光芒", "http://gl.ali213.net/html/2015-1/60303", 30187],
    # ["最终幻想13：雷霆归来", "http://gl.ali213.net/html/2015-12/96889", 30188],
    # ["圣斗士星矢：战士魂", "http://gl.ali213.net/html/2015-12/95307", 30189]
]

init_dict = {}

par_more = (
    re.compile(r'<p>更多相关资讯.+'),
    re.compile(r'<p></p>'),
    re.compile(r'<p>游戏专题[^<]+'),
    re.compile(r'<p>[^>]+213[^<]+</p>'))
par_need_del = ("\n", "\r", "　", "&#13;", "【游侠攻略组】")
par_in_title = [
    "",
    "图文攻略详解",
    "攻略秘籍_游侠网",
    "全关卡流程 + 全剧情 + 全收集",
    "全关卡流程+全剧情+全收集",
    "图文全流程攻略",
    "全主线+支线攻略",
    "全剧情",
    "全收集",
]

par_get_tag_from_title_re = re.compile(r'_.+')


def get_content(this_target_url):
    this_target = requests.get(this_target_url).content.decode("utf-8")

    # 页面描述信息
    title = pq(pq(this_target)("title")).text()
    for item_p in par_in_title:
        title = title.replace(item_p, "")
    tag = re.sub(par_get_tag_from_title_re, "", title)

    # 页面内容
    content_html = pq(pq(this_target)("div"))(".glzjshow_con")
    text = pq(content_html).html()
    for par_item in par_more:
        text = re.sub(par_item, '', text)
    abstract = pq(text).text()[:100] + "..."
    thumb = pq(pq(text)("img")[0]).attr("src")
    if thumb == "":
        print("NO PICTURE!")
    text = html.escape(text, quote=True)
    c_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    page_view = int(random.uniform(100, 5000))
    new_doc = Docs([title, text, abstract, c_time, "", page_view, tag, init_dict["game_name"], thumb])

    logging.debug(thumb)
    logging.debug("\n\n")

    db.session.add(new_doc)
    db.session.commit()


if __name__ == '__main__':
    for game in game_target:

        init_dict["url_head"] = game[1]
        init_dict["game_name"] = game[0]
        print(type(init_dict["game_name"]))
        par_in_title[0] = "_" + init_dict["game_name"]
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

            if page_number > 3:
                break
