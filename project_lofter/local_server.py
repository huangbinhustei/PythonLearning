# -*- coding: utf-8 -*-

from flask import Flask, request, url_for, redirect
from flask import render_template
import os
from collections import defaultdict
import logging

app = Flask(__name__)
path = os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/static/"
pic_dict = defaultdict(lambda: 0)


@app.route("/static", methods=["GET"])
def me_static():
    blogger = next(os.walk(path))
    blogger = blogger[1]
    html_static = ""
    for blog_name in blogger:
        html_static += "<p><a href=\"/static/" + blog_name + "\">" + blog_name + "</a></p>"
    logging.debug(html_static)
    return html_static


@app.route("/static/<blog_name>", methods=["GET"])
def me_blog(blog_name):
    posts = next(os.walk(path + "/" + blog_name))

    post_list = []
    for item in posts[1]:
        imgs = next(os.walk(path + "/" + blog_name + "/" + item))[2]
        if not imgs:
            continue
        img = imgs[0]
        if not img:
            continue
        elif img[:3] == "txt":
            continue
        temp = ["static/" + blog_name +"/" + item, blog_name + "/" + item + "/" + img]
        print (temp)
        post_list.append(temp)
    return render_template("me_blog.html", post_list=post_list)


@app.route("/static/<blog_name>/<post_name>", methods=["GET"])
def me_post(blog_name, post_name):
    pics = next(os.walk(path + "/" + blog_name + "/" + post_name))
    pics = pics[2]
    html_pic = ""
    html_head = "<img src=\"/static/" + blog_name + "/" + post_name + "/"
    for pic_name in pics:
        html_pic += html_head + pic_name + "\"><p></p>"
    logging.debug(html_pic)
    return html_pic


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
