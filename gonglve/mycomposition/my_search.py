#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jieba
import heapq
from collections import defaultdict
from data import Docs, Keywords, db, app, cost_count


@cost_count
def search_by_title(my_query, topx=10):
    outputs = defaultdict(lambda: 0)
    key_words = set(jieba.cut(my_query, cut_all=False))
    for line in Keywords.query.filter(Keywords.key.in_(key_words)):
        docs, weight = line.docs.split(","), line.weight
        for doc_id in docs:
            outputs[doc_id] += weight

    outputs = heapq.nlargest(topx * 3, outputs.items(), lambda x: x[1])

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
