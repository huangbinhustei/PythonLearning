#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jieba
import math
import os
from datetime import datetime
from collections import defaultdict
import sqlite3

# 第一步：生成词典
start = datetime.now()
user_dict = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/user_dict/game_name_list.txt"
init_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/doc_list.txt"
update_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/doc_list_mini.txt"
num_of_rows = 1000000 * 2.7  # len(title_list)


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
        print("database_create")
        print(e)
        flag = False
    finally:
        cursor.close()
        connect.commit()
        connect.close()
        return flag


def database_merge(target_list, is_init=False):
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
                pass
                cursor.execute(
                        'update keywords(key,key_weight,docs,games) values (?,?,?,?)', (a0, a1, a2, a3))

    except Exception as e:
        print("database_merge")
        print(e)
        flag = False
    finally:
        cursor.close()
        connect.commit()
        connect.close()
    return flag


with open(user_dict, "r", encoding="utf-8") as ud:
    for line in ud.readlines():
        xxx = line.strip()
        jieba.add_word(xxx)


def default_weight():
    # 权重词典的定义如下：
    # 第0位(float):表示权重
    # 第1位(list)：内有包含这个keywords的所有标题
    # 第2位(list)：内有包含这个keywords的所有游戏名
    return [0, [], []]


def load_doc_list(this_path):
    with open(this_path, "r", encoding="utf-8") as tl:
        title_list = tl.readlines()
    return title_list


def weight_calc(this_title_list):
    total_key_words = defaultdict(default_weight)

    for lines in this_title_list:
        titles = lines.split("\t")
        temp = jieba.cut(titles[1], cut_all=False)
        for keyword in temp:
            total_key_words[keyword][1].append(titles[0])  # 权重表存入 doc_id
            total_key_words[keyword][2].append(titles[2].strip())  # 权重表存入 game_name
    for words in total_key_words:
        total_key_words[words][2] = list(set(total_key_words[words][2]))
        title_count = len(total_key_words[words][1])
        game_name_count = len(total_key_words[words][2])
        total_key_words[words][0] = math.log(num_of_rows / title_count / game_name_count)

    dict_keywords_weight_docs_games = dict(
            (k, v) for k, v in total_key_words.items() if (
                v[0] > 0 and len(v[1]) > 4 and len(k) > 1
            )
    )

    return dict_keywords_weight_docs_games


def weight_database_init():
    database_create()
    title_list_of_init = load_doc_list(init_path)
    dict_init = weight_calc(title_list_of_init)
    database_merge(dict_init, is_init=True)


def weight_database_update():
    title_list_of_update = load_doc_list(update_path)
    dict_update = weight_calc(title_list_of_update)
    database_merge(dict_update, is_init=False)


if __name__ == '__main__':
    weight_database_init()
