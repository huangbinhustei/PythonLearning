# -*- coding: utf-8 -*-

# from header_tieba import Tieba
from pyquery import PyQuery as pq
import time
import random
import html
import requests
import re
import logging
logging.basicConfig(level=logging.INFO)


def init_s():
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'tieba.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36',
    }
    s.headers.update(header)
    s.verify = False


def get_categories():
    home_page_response = s.get(url)
    home_page = home_page_response.content
    html_categories = pq(pq(home_page)(".class_list"))("a")
    categories = []
    for category in html_categories:
        categories.append([pq(category).text(), pq(category).attr("href")])
    return categories


if __name__ == '__main__':
    url = "http://tieba.baidu.com/f/index/forumpark?pcn=%D3%CE%CF%B7&pci=0&ct=1&rn=20&pn=1"
    s = requests.session()
    init_s()

    par = dict()

    for item in get_categories():
        print(item)
        list_1 = item[1].split("?")
        start_url = "http://tieba.baidu.com" + list_1[0]
        for i in list_1[1].split("&"):
            list_i = i.split("=")
            par[list_i[0]] = list_i[1]

    for k, v in par.items():
        print(k + "\t" + v)





