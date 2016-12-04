#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from pyquery import PyQuery as pq
from data import Docs, db
import time

start_url = "http://gl.baidu.com/zuowen"
magic = "&pn="
i = 0
while 1:
    if 0 == i:
        url = start_url
    else:
        url = start_url + magic + str(i)
    print(url)
    time.sleep(0.2)
    list_response = requests.get(url)
    if list_response.status_code != 200:
        print("抓不了")
        break
    for item in pq(list_response.content)(".item-content"):
        title = pq(item)(".title")("a").text()
        temp = pq(item)(".com-info")(".tag")
        grade = pq(temp[0]).text()
        genre = pq(temp[1]).text()
        words = pq(temp[2]).text()
        former_url = pq(item)("a").attr("href")
        md = former_url.replace("/view/", "")
        r = requests.get("http://gl.baidu.com" + former_url)
        if r.status_code != 200:
            print("内容页抓不了")
            break
        c = r.content
        content = pq(c)(".doc-content-main-wrap").text()
        author = pq(c)(".doc-info").text().split(" ")[-1]
        now = int(time.time())*1000000
        new_doc = Docs([md, title, content, grade, genre, words, "", author, 0, 0, 0, now, now, former_url, "攻略"])
        db.session.add(new_doc)
        db.session.commit()
    i += 1
