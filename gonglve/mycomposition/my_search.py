#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jieba
import os
from collections import defaultdict
import math
from data import Docs, Keywords, db, app, cost_count, basedir, Titles

jieba.initialize()


@cost_count
def load_doc_weight():
    doc_dict = defaultdict(lambda: 0)
    with open(os.path.join(basedir, "id_weight.txt"), "r", encoding="utf-8") as f:
        for line in f.readlines():
            item = line.strip().split("\t")
            doc_dict[item[0]] = float(item[1])
    return doc_dict

id_weight = load_doc_weight()


@cost_count
def search_by_title(my_query, topx=10, need_same=False):
    outputs = defaultdict(lambda: 0)
    key_words = list(jieba.cut(my_query, cut_all=False))
    query_weight = 0
    for line in Keywords.query.filter(Keywords.key.in_(key_words)):
        docs, weight = line.docs.split(","), line.weight
        for doc_id in docs:
            outputs[doc_id] += weight * weight * key_words.count(line.key)
        query_weight += weight * weight * key_words.count(line.key)
    if not need_same:
        outputs_c = outputs.copy()
        bad_titles = Titles.query.get(my_query)
        if bad_titles:
            bad_titles = bad_titles.docs.split(",")
            for k, v in outputs_c.items():
                if k in bad_titles:
                    del outputs[k]

    outputs = sorted(outputs.items(), key=lambda doc: doc[1] / math.sqrt(id_weight[doc[0]]), reverse=True)[:topx]
    outputs = [[item[0], item[1]/math.sqrt(id_weight[item[0]])/math.sqrt(query_weight)] for item in outputs]
    return outputs


if __name__ == '__main__':
    while 1:
        a = input("query\n")
        if a == "Q":
            break
        search_by_title(a)
