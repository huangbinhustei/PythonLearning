import heapq
import jieba
import os
from datetime import datetime
from collections import defaultdict

start = datetime.now()
user_dict = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/userdict/gamename.txt"
result_file = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/weight.txt"


def weight_init():
    # 权重词典的定义如下：
    # 第0位(int):表示权重
    # 第1位(list)：内有包含这个keywords的所有标题
    # 第2位(list)：内有包含这个keywords的所有游戏名
    return [0, [], []]


weights = defaultdict(weight_init)

with open(result_file, "r", encoding="utf-8") as w:
    for line in w:
        temp = line.split("\t")
        weights[temp[0]][0] = float(temp[1])
        weights[temp[0]][1] = temp[2][1:-2].split(",")
        weights[temp[0]][2] = temp[3].strip().split(",")

with open(user_dict, "r", encoding="utf-8") as ud:
    for line in ud.readlines():
        xxx = line.strip()
        jieba.add_word(xxx)

mid = datetime.now()
print(mid-start)


def do_sug(target):
    outputs = defaultdict(lambda: 0)
    key_words = set(jieba.cut(target, cut_all=False))
    for items in key_words:
        weight = weights[items][0]
        if weight <= 0:
            continue
        for title in set(weights[items][1]):
            outputs[title] += weight
    for_print = heapq.nlargest(10, outputs.items(), lambda x: x[1])
    for item in for_print:
        print("\t" + str(item[0]) + "\t" + str(item[1]))


while True:
    query = input("Query, please!\n")
    if query == "exit":
        print("See you!")
        break
    do_sug(query)
