#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jieba
import math
import os
from datetime import datetime
from collections import defaultdict
import sqlite3
from multiprocessing import Process, Queue, Pool, Manager
from time import sleep, ctime

user_dict = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/user_dict/game_name_list.txt"
init_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/doc_list.txt"
update_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/doc_list_mini.txt"
num_of_rows = 1000000 * 2.7  # 暂时用来替代 len(title_list)


def database_create():
    connect = sqlite3.connect("weight.db")
    cursor = connect.cursor()
    flag = True

    try:
        cursor.execute(
                'create table keywords'
                '(key varchar(20) primary key,key_weight float,docs varchar(2000),games varchar(900))'
        )
    except Exception as e:
        print("error: " + str(e) + " @ database_create")
        flag = False
    finally:
        cursor.close()
        connect.commit()
        connect.close()
        return flag


def database_merge(target_list, is_init=False):
    print("merge begin @ " + str(ctime()))
    connect = sqlite3.connect("weight.db")
    cursor = connect.cursor()
    flag = True
    try:
        for item in target_list:
            a0 = item
            a1 = target_list[item][0]
            a2 = ",".join(target_list[item][1])
            a3 = ",".join(target_list[item][2])

            if is_init:
                cursor.execute(
                        'insert into keywords(key,key_weight,docs,games) values (?,?,?,?)', (a0, a1, a2, a3))
            else:
                pass    # 如果有主键则 update，否则 insert。

    except Exception as e:
        print("error: " + str(e) + " @ database_merge")
        flag = False
    finally:
        cursor.close()
        connect.commit()
        connect.close()
    print("merge end @ " + str(ctime()))
    return flag


def load_user_dict():
    with open(user_dict, "r", encoding="utf-8") as ud:
        for line in ud.readlines():
            xxx = line.strip()
            jieba.add_word(xxx)


def default_weight():
    # 权重词典的定义如下：
    # 第0位(float):表示权重
    # 第1位(list)：内有包含这个keywords的所有标题
    # 第2位(list)：内有包含这个keywords的所有游戏名
    return [0, set([]), set([])]


def load_doc_list(this_path):
    with open(this_path, "r", encoding="utf-8") as tl:
        title_list = tl.readlines()
        # title_list 格式是：doc_id,doc_title,doc_game_name
    return title_list


def weight_calc(this_title_list):
    total_key_words = defaultdict(default_weight)

    for lines in this_title_list:
        titles = lines.split("\t")
        temp = jieba.cut(titles[1], cut_all=False)
        for keyword in temp:
            total_key_words[keyword][1].add(titles[0])  # 权重表存入 doc_id
            total_key_words[keyword][2].add(titles[2])  # 权重表存入 game_name

    dict_keywords_weight_docs_games = dict(
            (k, v) for k, v in total_key_words.items()
            # (k, v) for k, v in total_key_words.items() if (
            #     v[0] > 0 and len(v[1]) > 4 and len(k) > 1
            # )
    )

    return dict_keywords_weight_docs_games


def weight_database_init():
    title_list_of_init = load_doc_list(init_path)
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
        print(i)
        p.apply_async(for_process, args=(title_list_of_init_half[i], dict_init_queue))
    p.close()

    # p_fi = Process(target=for_process, args=(title_list_of_init_half[0], dict_init_queue))
    # p_se = Process(target=for_process, args=(title_list_of_init_half[1], dict_init_queue))
    # p_th = Process(target=for_process, args=(title_list_of_init_half[2], dict_init_queue))
    # p_fi.daemon = True
    # p_se.daemon = True
    # p_th.daemon = True
    # p_fi.start()
    # p_se.start()
    # p_th.start()

    dict_init = defaultdict(default_weight)
    process_count = 0
    while 1:
        a1 = dict_init_queue.get()
        this_key_word = a1[0]
        if a1 == "stop":
            process_count += 1
            if process_count == 3:
                break
            else:
                continue
        if this_key_word in dict_init:
            dict_init[this_key_word][1] = dict_init[this_key_word][1] | a1[2]
            dict_init[this_key_word][2] = dict_init[this_key_word][2] | a1[3]
        else:
            dict_init[this_key_word] = [a1[1], a1[2], a1[3]]
    for words in dict_init:
        title_count = len(dict_init[words][1])
        game_name_count = len(dict_init[words][2])
        dict_init[words][0] = math.log(num_of_rows / title_count / game_name_count)
    database_merge(dict_init, is_init=True)


def for_process(this_list, this_queue):
    print(str(os.getpid()) + " 子进程启动 @:" + str(ctime()))
    temp_dict = weight_calc(this_list)
    for item in temp_dict:
        list_1 = [item, temp_dict[item][0], temp_dict[item][1], temp_dict[item][2]]
        this_queue.put(list_1)
    this_queue.put("stop")
    print(str(os.getpid()) + " 子进程结束 @:" + str(ctime()))


def weight_database_update():
    title_list_of_update = load_doc_list(update_path)
    dict_update = weight_calc(title_list_of_update)
    database_merge(dict_update, is_init=False)


if __name__ == '__main__':
    start = datetime.now()
    database_create()   # 创建表
    weight_database_init()
    print(datetime.now()-start)

# test @ 1: time = 0:01:13.443222 = 73秒
