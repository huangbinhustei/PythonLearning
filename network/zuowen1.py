#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import heapq
import jieba
import os
import re
from pyquery import PyQuery as pq
from datetime import datetime
from collections import defaultdict
import threading

start = datetime.now()
zuowen_title_file = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/zuowentitle.txt"
result_file = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/final.txt"

hahaha = []
ci = []

with open(zuowen_title_file, "r", encoding="utf-8") as w:
    for line in w:
        temp = line.split("\t")
        ci.append(temp[0])

while 1:
    if not ci:
        break
    item = ci.pop()
    url_item = "http://www.baidu.com/s?ie=UTF-8&wd=" + item
    target = pq(url = url_item)
    me_h3 = pq(target)("h3")
    i = 0
    for xxxa in pq(me_h3):
        i += 1
        if(i == 2):
            break
        xxxxb = pq(xxxa).text()
        if (xxxxb.find("作文") > -1):
            xxxxc = item.strip() + "\t" + xxxxb
            print(xxxxc)
            hahaha.append(xxxxb)

with open(result_file, "w", encoding="utf-8") as w1:
    for item in hahaha:
    	w1.write(item + "\n")
