#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import heapq

import math
import os

user_dict = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/userdict/gamename.txt"
path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/doclist_all.txt"

import jieba
jieba.load_userdict(user_dict)
print(jieba.load_userdict(user_dict))

from datetime import datetime
from contextlib import closing
from collections import defaultdict


target = "天天炫斗商城系统详解介绍攻略"

jieba.add_word("天天炫斗")
jieba.del_word("商城")

key_words = set(jieba.cut(target, cut_all=False))
print(key_words)
L2 = []
start = datetime.now()
with open(path, "r", encoding="utf-8") as query:
    table = set(query.readlines())
    weight = defaultdict(lambda: 0)
    contain = defaultdict(lambda: 0)

    for L1 in table:
        for keyw in key_words:
            if L1.count(keyw):
                weight[keyw] += L1.count(keyw)
    for keyw in key_words:
        weight[keyw] = math.log(len(table) / weight[keyw])
#        if k < 3:
#            weight[k] += 3
    for L1 in table:
        for keyw in key_words:
            contain[L1] += L1.count(keyw) * weight[keyw] / len(key_words)


for_print = heapq.nlargest(10, contain.items(), lambda x: x[1])


print(datetime.now() - start)
for xxx in for_print:
    print(xxx)
