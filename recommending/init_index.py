#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import heapq
import jieba
import math
import os
from datetime import datetime
from collections import defaultdict

# 第一步：生成词典
start = datetime.now()
user_dict = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/userdict/gamename.txt"
path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/doclist_all.txt"
result_file = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/weight.txt"

with open(user_dict, "r", encoding="utf-8") as ud:
    for line in ud.readlines():
        xxx = line.strip()
        jieba.add_word(xxx)


def weight_init():
    # 权重词典的定义如下：
    # 第0位(int):表示权重
    # 第1位(list)：内有包含这个keywords的所有标题
    # 第2位(list)：内有包含这个keywords的所有游戏名
    return [0, [], []]


total_key_words = defaultdict(weight_init)


def weight_calc():
    with open(path, "r", encoding="utf-8") as tl:
        title_list = set(tl.readlines())
        num_of_rows = len(title_list)
        for lines in title_list:
            titles = lines.split("\t")
            temp = jieba.cut(titles[0], cut_all=False)
            for keyword in temp:
                total_key_words[keyword][1].append(titles[0])
                total_key_words[keyword][2].append(titles[1].strip())
        for words in total_key_words:
            total_key_words[words][2] = list(set(total_key_words[words][2]))
            title_count = len(total_key_words[words][1])
            game_name_count = len(total_key_words[words][2])
            total_key_words[words][0] = math.log(num_of_rows / title_count / game_name_count)


def weight_calc_save(need_save):
    with open(result_file, "w", encoding="utf-8") as rf:
        for item in need_save:
            a1 = ",".join(item[1][1])
            a2 = ",".join(item[1][2])
            rf.write(item[0] + "\t" + str(item[1][0]) + "\t" + a1 + "\t" + a2 + "\n")


weight_calc()

bigger = dict((k, v) for k, v in total_key_words.items() if (v[0] > 0 and len(v[1]) > 1))
order_bigger = heapq.nlargest(len(bigger), bigger.items(), lambda x: x[1])

weight_calc_save(order_bigger)
print(datetime.now() - start)
