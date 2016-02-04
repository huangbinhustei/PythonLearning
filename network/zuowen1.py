#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import heapq
import os
import re
from pyquery import PyQuery as pq
from datetime import datetime
from collections import defaultdict
import threading

zuowen_title_file = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/zuowentitle.txt"
result_file = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/final.txt"


ci = []


def init_final():
    return [[],[]]

final_query = defaultdict(init_final)

with open(zuowen_title_file, "r", encoding="utf-8") as w:
    for line in w:
        ci.append(line)
        # temp = line.split("\t")
        # ci.append(temp[0])

while 1:
    if not ci:
        break
    query = ci.pop()
    url_item = "http://www.baidu.com/s?ie=UTF-8&wd=" + query
    target = pq(url=url_item)
    me_h3 = pq(target)("h3")
    for item in me_h3:
        temp1 = pq(item).text()
        final_query[query][0].append(temp1)
    me_url = pq(target)(".c-showurl")
    for item1 in me_url:
        temp2 = pq(item1).text()
        final_query[query][1].append(temp2)

# for xxxxa in final_query:
#     print(xxxxa)
#     print(len(final_query[xxxxa][0]))
#     print(len(final_query[xxxxa][1]))

with open(result_file, "w", encoding="utf-8") as w1:
    for each_query in final_query:
        if len(final_query[each_query][0]) == len(final_query[each_query][1]):
            for ind in range(len(final_query[each_query][0])):
                w1.write(each_query.strip() + "\t" + final_query[each_query][0][ind] + "\t" + final_query[each_query][1][ind] + "\n")
        else:
            print(each_query)
