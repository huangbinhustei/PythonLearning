#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jieba
import math
import os
from collections import defaultdict
from multiprocessing import Pool, Manager
from time import sleep, ctime
from data import Docs, Keywords, db, app, cost_count, Titles
basedir = os.path.abspath(os.path.dirname(__file__))

num_of_titles = 289581      # = select count(DISTINCT title) from docs;


def default_weight():
    # 权重词典的定义如下：
    # 第0位(float):表示权重
    # 第1位(list)：内有包含这个keywords的所有标题
    return [0, set([])]


@cost_count
def database_merge(target_list):
    for key, v in target_list.items():
        ids = [str(item) for item in v[1]]
        new_key = Keywords([key, v[0], ",".join(ids)])
        try:
            db.session.add(new_key)
        except:
            print(key)
    db.session.commit()


@cost_count
def for_process(this_list, this_queue):
    print(str(os.getpid()) + " 子进程启动 @:" + str(ctime()))
    temp_dict = weight_calc(this_list)
    for key, v in temp_dict.items():
        # 为什么我要把词典拆分成数组放到队列里面去？
        list_1 = [key, v[0], v[1]]
        this_queue.put(list_1)
    this_queue.put("stop")
    print(str(os.getpid()) + " 子进程结束 @:" + str(ctime()))


@cost_count
def weight_calc(this_title_list):
    total_key_words = defaultdict(default_weight)

    for line in this_title_list:
        title, doc_md = line[0], line[1]
        for keyword in jieba.cut(title, cut_all=False):
            total_key_words[keyword][1].add(doc_md)  # 权重表存入 doc_id

    return total_key_words


@cost_count
def weight_database_init():
    """
    生成倒排表，key / key的权重 / 包含这个key的doc
    """
    title_list_of_init = [[item.title, item.doc_id] for item in Docs.query.all()]
    mid = int(len(title_list_of_init)/3)
    title_list_of_init_half = [
        title_list_of_init[0:mid + 1],
        title_list_of_init[mid:mid * 2 + 1],
        title_list_of_init[mid * 2:-1]
    ]
    ma = Manager()
    dict_init_queue = ma.Queue()

    p = Pool(3)
    for i in range(3):
        p.apply_async(for_process, args=(title_list_of_init_half[i], dict_init_queue))
    p.close()

    dict_init = defaultdict(default_weight)
    process_count = 0
    while 1:
        a1 = dict_init_queue.get()
        # a1 格式： [keyword, weights, docs]
        this_key_word = a1[0]
        if a1 == "stop":
            process_count += 1
            if process_count == 3:
                break
            else:
                continue
        if this_key_word in dict_init:
            dict_init[this_key_word][1] = dict_init[this_key_word][1] | a1[2]
        else:
            dict_init[this_key_word] = [a1[1], a1[2]]
    for words in dict_init:
        title_count = len(dict_init[words][1])
        dict_init[words][0] = math.log(num_of_titles / title_count)
    database_merge(dict_init)


def titles_init():
    doc_dict = defaultdict(lambda: [])
    for doc in [[item.title, item.doc_id] for item in Docs.query.all()]:
        doc_dict[doc[0]].append(doc[1])
    for k, v in doc_dict.items():
        if k == "":
            continue
        if len(v) == 1:
            continue
        new_row = Titles([k, ",".join([str(item) for item in v])])
        db.session.add(new_row)
    db.session.commit()


@cost_count
def load_docs():
    return Docs.query.all()


@cost_count
def load_keywords():
    return Keywords.query.all()


@cost_count
def title_weight_count():
    doc_dict = defaultdict(lambda: 0)
    key_dict = defaultdict(lambda: 0)
    all_keys = load_keywords()
    for item in all_keys:
        key_dict[item.key] = item.weight
    for item in load_docs():
        for keyword in jieba.cut(item.title, cut_all=False):
            doc_dict[item.doc_id] += key_dict[keyword]

    return doc_dict
    # with open(os.path.join(basedir, "id_weight.txt"), "w", encoding="utf-8") as f:
    #     for k, v in doc_dict.items():
    #         f.write(str(k) + "\t" + str(v)+"\n")

if __name__ == '__main__':
    input("不管如何，三思而后行！")
    # pass
    # title_weight_count()
    # titles_init()
    # weight_database_init()

