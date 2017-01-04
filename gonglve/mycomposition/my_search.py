#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jieba
import heapq
import os
from collections import defaultdict
from data import Docs, Keywords, db, app, cost_count, basedir


@cost_count
def load_doc_weight():
    doc_dict = defaultdict(lambda: 0)
    with open(os.path.join(basedir, "id_weight.txt"), "r", encoding="utf-8") as f:
        for line in f.readlines():
            item = line.strip().split("\t")
            doc_dict[item[0]] = float(item[1])
    print(doc_dict[2])
    return doc_dict


@cost_count
def search_by_title(my_query, topx=10, need_same=False):
    # self_id = Docs.query.filter(Docs.title == my_query).first()
    # if self_id:
    #     self_id = self_id.doc_id
    # doc_dict = load_doc_weight()
    outputs = defaultdict(lambda: 0)
    key_words = set(jieba.cut(my_query, cut_all=False))
    for line in Keywords.query.filter(Keywords.key.in_(key_words)):
        docs, weight = line.docs.split(","), line.weight
        for doc_id in docs:
            outputs[doc_id] += weight
    if not need_same:
        for k, v in outputs.items():
            if my_query == v:
                del outputs[k]
    # for k, v in outputs.items():
    #     outputs[k] = v/doc_dict[k]/doc_dict[str(self_id)]

    return heapq.nlargest(topx, outputs.items(), lambda x: x[1])


if __name__ == '__main__':
    while 1:
        a = input("query\n")
        if a == "Q":
            break
        search_by_title(a)
