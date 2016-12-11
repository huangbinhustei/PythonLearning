#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from pyquery import PyQuery as pq
from data import Docs, db
import threading
import time
import logging
import os
logging.basicConfig(level=logging.INFO)


def loading_things_has_done():
    logging.info("开始统计历史抓取记录")
    a = time.time()
    set_md5s = set([item.doc_md for item in Docs.query.all()])
    b = time.time()
    logging.info("统计完成，共" + str(len(set_md5s)) + "条记录，耗时：" + str(b - a)[:5] + "秒")
    return set_md5s


def view_spider(view_block, _records):
    title = pq(view_block)(".title")("a").text()
    temp = pq(view_block)(".com-info")(".tag")
    grade = pq(temp[0]).text()
    genre = pq(temp[1]).text()
    words = pq(temp[2]).text()
    former_url = pq(view_block)("a").attr("href")
    md = former_url.replace("/view/", "")
    if md in _records:
        return
    r = requests.get("http://gl.baidu.com" + former_url)
    if r.status_code != 200:
        print("内容页抓不了")
        return
    c = r.content
    content = pq(c)(".doc-content-main-wrap").text()
    author = pq(c)(".doc-info").text().split(" ")[-1]
    now = int(time.time()) * 1000000
    new_doc = Docs([md, title, content, grade, genre, words, "", author, 0, 0, 0, now, now, former_url, "攻略"])
    db.session.add(new_doc)
    db.session.commit()


def list_spider(start_url, i, _records):
    magic = "?pn="
    while 1:
        if 0 == i:
            url = start_url
        else:
            url = start_url + magic + str(i)
        print(url)
        time.sleep(0.5)
        list_response = requests.get(url)
        if list_response.status_code != 200:
            print("抓不了")
            break
        blocks = pq(list_response.content)(".item-content")
        if not blocks:
            print("被防抓了 or 抓完了")
            continue
        th = []
        for block in blocks:
            th.append(threading.Thread(target=view_spider, args=(block, _records,)))
        for t in th:
            t.setDaemon(True)
            t.start()
        for t in th:
            t.join()
        i += 1
        with open(os.path.join(os.path.abspath("."), "spider_log.txt"), "w") as fs:
            fs.write(str(i - 1))


if __name__ == '__main__':
    with open(os.path.join(os.path.abspath("."), "spider_log.txt"), "r") as f:
        page = int(f.read().strip())
    records = set([]) if True else loading_things_has_done()
    list_spider("http://gl.baidu.com/zuowen", page, records)
