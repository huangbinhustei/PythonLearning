#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jieba
import os
from collections import defaultdict
import math
from data import Docs, Keywords, Weights, Grade, Genre, db, app, cost_count, basedir, Sugs
import logging
logging.basicConfig(level=logging.WARNING)

jieba.initialize()
page_len = app.config["POST_IN_SINGLE_PAGE"]
page_preload_count = 10
genre_right = {0, 1, 2, 4,}
grade_right = {10, 11, 12}


@cost_count
def load_doc_weight():
    doc_dict = defaultdict(float)
    with open(os.path.join(basedir, "id_weight.txt"), "r", encoding="utf-8") as f:
        for line in f.readlines():
            item = line.strip().split("\t")
            doc_dict[item[0]] = float(item[1])
    return doc_dict
id_weight = load_doc_weight()


@cost_count
def search_by_title(my_query,
                    topx=page_len * page_preload_count,
                    washer=defaultdict(int),
                    ):
    outputs, query_weight = search_no_rank(my_query)
    outputs = search_washer(outputs, washer)

    outputs = sorted(outputs.items(), key=lambda doc: doc[1] / id_weight[doc[0]], reverse=True)[:topx]
    outputs = [[item[0], item[1] / id_weight[item[0]] / query_weight] for item in outputs]

    result_search = []
    for line in outputs:
        doc_id, doc_value = line[0], str(line[1])
        result_search.append([str(doc_value)[:8], Docs.query.get(doc_id)])
    return result_search


def search_no_rank(_query_):
    outputs = defaultdict(int)
    key_words = jieba.lcut_for_search(_query_)
    query_weight = 0
    for line in Keywords.query.filter(Keywords.key.in_(key_words)):
        docs, weight = line.docs.split(","), line.weight
        for doc_id in docs:
            outputs[doc_id] += weight * weight * key_words.count(line.key)
        query_weight += weight * weight * key_words.count(line.key)
    query_weight = math.sqrt(query_weight)
    return outputs, query_weight


def search_washer(res_dict, washer=defaultdict(int)):
    def filter_by_grade_and_genre(_res_dict_):
        idx = set([])
        for item in washer["grade"]:
            if item in grade_right:
                idx |= (Grade.query.get(item).get_docs())
            else:
                logging.error("type error: grade must be list made by int")
        idx_genre = set([])
        for item in washer["genre"]:
            if item in genre_right:
                idx_genre |= (Genre.query.get(item).get_docs())
            else:
                logging.error("type error: genre must be int or list")
        if idx == set([]):
            idx = idx_genre
        elif idx_genre != set([]):
            idx &= idx_genre
        if idx:
            for t_key, t_value in _res_dict_.copy().items():
                if int(t_key) not in idx:
                    del _res_dict_[t_key]
        return _res_dict_

    def remove_same_titles(_res_dict_):
        bad_titles = washer["id_need_del"]
        if bad_titles:
            for k, v in _res_dict_.copy().items():
                if int(k) in bad_titles:
                    del _res_dict_[k]
        return _res_dict_

    if washer["remove_same"]:
        res_dict = remove_same_titles(res_dict)
    if washer["filter"]:
        res_dict = filter_by_grade_and_genre(res_dict)

    return res_dict


if __name__ == '__main__':
    while 1:
        a = input("query\n")
        if a == "Q":
            break
        search_by_title(a)
