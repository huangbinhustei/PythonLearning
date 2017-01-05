#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jieba
import heapq
import os
from collections import defaultdict
from data import Docs, Keywords, db, app, cost_count, basedir, Titles


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
    id_weight = defaultdict(lambda: 0)
    key_words = list(jieba.cut(my_query, cut_all=False))
    for line in Keywords.query.filter(Keywords.key.in_(key_words)):
        docs, weight = line.docs.split(","), line.weight

        for doc_id in docs:
            outputs[doc_id] += weight * key_words.count(line.key)
    if False == need_same:
        outputs_c = outputs.copy()
        bad_titles = Titles.query.get(my_query)
        if bad_titles:
            bad_titles = bad_titles.docs.split(",")
            for k, v in outputs_c.items():
                if k in bad_titles:
                    del outputs[k]
    
    outputs = sorted(outputs.items(), key=lambda k :(k[1], k[1]/len(k[0])),reverse=True)[:topx]
    # outputs = heapq.nlargest(topx, outputs.items(), lambda x: x[1])
    return outputs

    # sug_result = []
    # for doc_id, doc_value in outputs:
    #     self_weight = 0
    #     print(str(doc_id))
    #     for self_keys in set(jieba.cut(Docs.query.get(doc_id).title, cut_all=False)):
    #         try:
    #             self_weight += Keywords.query.get(self_keys).weight
    #         except:
    #             pass
    #     if self_weight == 0:
    #         continue
    #     sug_result.append([int(doc_id), doc_value/self_weight])

    # return heapq.nlargest(topx, sug_result, lambda x: x[1])


if __name__ == '__main__':
    while 1:
        a = input("query\n")
        if a == "Q":
            break
        search_by_title(a)
