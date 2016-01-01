import heapq
import jieba
import os
# from datetime import datetime
from collections import defaultdict
import sqlite3

user_dict = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/user_dict/game_name_list.txt"
path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/doc_list.txt"


def weight_init():
    # 权重词典的定义如下：
    # 第0位(float):表示权重
    # 第1位(list)：内有包含这个keywords的所有标题
    # 第2位(list)：内有包含这个keywords的所有游戏名
    return [0, [], []]


weights = defaultdict(weight_init)
doc_dict = defaultdict(lambda: "")


def load_dict_of_id2title():
    with open(path, "r", encoding="utf-8") as docs:
        for line in docs:
            temp = line.split("\t")
            doc_dict[str(temp[0])] = temp[1]


def init_self():
    with open(user_dict, "r", encoding="utf-8") as ud:
        for line in ud.readlines():
            xxx = line.strip()
            jieba.add_word(xxx)


def segmentation2sql(sentence):
    key_words = set(jieba.cut(sentence, cut_all=False))
    temp = []
    for item in key_words:
        if item != " ":
            temp.append("\"" + item + "\"")
    return "select key,key_weight,docs from keywords where key in (" + ",".join(temp) + ")"


def format_ans(list_target):
    sug_result = []
    for_print = heapq.nlargest(10, list_target.items(), lambda x: x[1])
    for item in for_print:
        true_name = doc_dict[str(item[0])]
        print("\t" + true_name + "\t" + str(item[1]))
        sug_result.append("\t" + true_name + "\t" + str(item[1]))
    return sug_result


def do_sug(target):
    outputs = defaultdict(lambda: 0)

    str_sql = segmentation2sql(target)
    conn = sqlite3.connect("weight.db")
    cursor = conn.cursor()
    try:
        cursor.execute(str_sql)
        values_temp = cursor.fetchall()
        for sql_item in values_temp:
            if not sql_item:
                continue
            weight = values_temp[0][1]
            for doc_id in str(values_temp[0][2]).split(","):
                outputs[doc_id] += weight
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.commit()
        conn.close()

    for key in outputs:
        outputs[key] /= len(key) + 1

    return format_ans(outputs)


def me_main(query_trans_in):
    init_self()
    load_dict_of_id2title()
    return do_sug(query_trans_in)
