#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jieba
import os
from collections import defaultdict
import math
from data import Docs, Keywords, Grade, Genre, db, app, Titles, cost_count, basedir
import logging
logging.basicConfig(level=logging.ERROR)

jieba.initialize()
page_len = app.config["POST_IN_SINGLE_PAGE"]
page_preload_count = 10


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
def search_by_title(my_query,
                    grade=-1,
                    genre=-1,
                    topx=page_len * page_preload_count,
                    need_same=True,
                    ):

    def filter_by_grade_and_genre(res_dict):
        if grade == [-1] and genre == [-1]:
            return res_dict
        else:
            idx = set([])
            if grade != [-1]:
                for item in grade:
                    if isinstance(item, int):
                        idx |= (Grade.query.get(item).get_docs())
                    else:
                        logging.error("type error: grade must be list made by int")
            new_idx = set([])
            if genre != [-1]:
                for item in genre:
                    if isinstance(item, int):
                        new_idx |= (Genre.query.get(item).get_docs())
                    else:
                        logging.error("type error: genre must be int or list")
            if idx == set([]):
                idx = new_idx
            elif new_idx != set([]):
                idx &= new_idx

            for t_key, t_value in res_dict.copy().items():
                if int(t_key) not in idx:
                    del res_dict[t_key]
            return res_dict

    outputs = defaultdict(lambda: 0)
    key_words = list(jieba.cut(my_query, cut_all=False))
    query_weight = 0
    for line in Keywords.query.filter(Keywords.key.in_(key_words)):
        docs, weight = line.docs.split(","), line.weight
        for doc_id in docs:
            outputs[doc_id] += weight * weight * key_words.count(line.key)
        query_weight += weight * weight * key_words.count(line.key)

    if not need_same:
        bad_titles = Titles.query.get(my_query)
        if bad_titles:
            bad_titles = bad_titles.docs.split(",")
            for k, v in outputs.copy().items():
                if k in bad_titles:
                    del outputs[k]

    outputs = filter_by_grade_and_genre(outputs)
    outputs = sorted(outputs.items(), key=lambda doc: doc[1] / math.sqrt(id_weight[doc[0]]), reverse=True)[:topx]
    outputs = [[item[0], item[1]/math.sqrt(id_weight[item[0]])/math.sqrt(query_weight)] for item in outputs]

    result_search = []
    for line in outputs:
        doc_id, doc_value = line[0], str(line[1])
        result_search.append([str(doc_value)[:8], Docs.query.get(int(doc_id))])
    return result_search


if __name__ == '__main__':
    while 1:
        a = input("query\n")
        if a == "Q":
            break
        search_by_title(a)
