#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from data import Docs, Grade, Genre, Sugs, Keywords, db, cost_count, ProgressBar, Sugs, basedir
from sqlalchemy import desc, or_
from collections import defaultdict
# from my_search import search_by_title, id_weight
import math
from slugify import UniqueSlugify
import re
import os
import jieba
import jieba.analyse


province = {"北京", "天津", "河北", "山西", "内蒙", "辽宁", "吉林", "黑龙", "上海", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南",
            "广东", "广西", "海南", "重庆", "四川", "贵州", "云南", "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆", "香港", "澳门", "台湾", ""}


@cost_count
def slugging():
    print("slugging begin")
    custom_slugify = UniqueSlugify(to_lower=True)
    custom_slugify.separator = '_'
    block_count = 0
    block_length = 10000
    b = [item for item in Docs.query.all()]
    while 1:
        block = b[block_count * block_length: (block_count + 1) * block_length]
        if len(block) == 0:
            break
        for zuowen in block:
            zuowen.doc_md = custom_slugify(zuowen.title)
        block_count += 1
        db.session.commit()


@cost_count
def duplicate():
    print("duplicating begin")
    dict_lines = defaultdict(lambda: [])
    lines = [item for item in Docs.query.order_by(desc(Docs.create_time)).all()]
    for line in lines:
        dict_lines[line.doc_md].append(line)
    thing_to_del = []
    for k, v in dict_lines.items():
        if len(v) > 1:
            for item in v[1:]:
                thing_to_del.append(item)
    print(str(len(thing_to_del)) + "rows need del")
    for item in thing_to_del:
        db.session.delete(item)
    db.session.commit()


@cost_count
def property_avoid():
    par = re.compile(r'''<p>[^/]*?高一[：:].+?</p>''')
    print("property_avoid begin")
    throw = ("<p>", "</p>", ":", "：")
    comp_with_property = [item for item in
                          Docs.query.filter(or_(Docs.content.like("%高一：%"), Docs.content.like("%高一:%")))]
    for item in comp_with_property:
        danger_part = ",".join(re.findall(par, item.content))
        writer_1 = danger_part.split("高一:")[-1].replace("</p>", "").strip()
        writer_2 = danger_part.split("高一：")[-1].replace("</p>", "").strip()
        writer = writer_1 if len(writer_1) < len(writer_2) else writer_2
        org = danger_part.replace(writer, "")
        for p in throw:
            org = org.replace(p, "")
        org = org.strip().replace("\t", "")

        danger_part2 = danger_part
        for p in throw[:2]:
            danger_part = danger_part.replace(p, "")
        danger_part = danger_part.strip().replace("\t", "")

        if "班" in writer:
            continue
        if "年级" in writer:
            continue
        if "（" in writer:
            continue
        if "）" in writer:
            continue
        if "(" in writer:
            continue
        if ")" in writer:
            continue
        if "中" in writer:
            continue

        flag = False

        if ((len(danger_part) - len(writer) - len(org)) < 10) and (10 > len(writer) > 0):
            if org[:2] in province:
                if len(org) < 50:
                    flag = True
            else:
                if len(org) < 20:
                    flag = True
        if flag:
            item.author = writer
            item.former_org = org
            item.content = item.content.replace(danger_part2, "")
    db.session.commit()
    print(len(comp_with_property))


@cost_count
def content_del():
    print("content_del begin")
    par_1 = re.compile("<p>[　 \t]+")
    par_2 = re.compile("[ 　\t]+</p>")
    need_del = {"%<p> %", "%<p>　%", "%<p>	%"}
    for par in need_del:
        for item in Docs.query.filter(Docs.content.like(par)):
            # print(item.content, file=f)
            temp = re.sub(par_1, "<p>", item.content)
            temp = re.sub(par_2, "</p>", temp)
            item.content = temp
        print("content_del end")
        db.session.commit()


@cost_count
def genre_grade_make():
    docs = Docs.query.all()
    outputs = defaultdict(lambda: [])
    outputs1 = defaultdict(lambda: [])
    for doc in docs:
        outputs[doc.grade].append(str(doc.doc_id))
        outputs1[doc.genre].append(str(doc.doc_id))
    for k, v in outputs.items():
        new_grade = Grade([k, ",".join(v)])
        db.session.add(new_grade)
    for k, v in outputs1.items():
        new_genre = Genre([k, ",".join(v)])
        db.session.add(new_genre)
    db.session.commit()


col_n = ("doc_id", "doc_md", "title", "content", "grade", "genre", "words", "tags", "author", "view", "yesterday_view",
         "today_view", "create_time", "update_time", "former_url", "former_org")


def db_txt():
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "all_doc.txt"), "w", encoding="utf-8") as f:
        f.write("\t".join(col_n) + "\n")
        for item in Docs.query.all():
            r = ""
            for key in col_n:
                r += str(item.to_dict()[key]) + "\t"
            r += "\n"
            f.write(r)


@cost_count
def sug_init():
    titles = defaultdict(lambda: [set([]), set([])])
    docs = [[doc.doc_id, doc.title] for doc in Docs.query.all()]

    for doc in docs:
        titles[doc[1]][0].add(doc[0])

    bar = ProgressBar(total=len(titles))
    washer = defaultdict(int)
    washer["remove_same"] = True
    for title, values in titles.items():
        washer["id_need_del"] = [int(item) for item in values[0]]
        values[1] = [line[1].doc_id for line in search_by_title(title, topx=20, washer=washer)]
        new_sug = Sugs([
            title,
            ",".join([str(item) for item in values[0]]),
            ",".join([str(item) for item in values[1]]),
        ])
        db.session.add(new_sug)
        bar.move()
    db.session.commit()


def set_status():
    all_key = set([item.key for item in Keywords.query.all()])
    docs = Docs.query.filter(Docs.status == 1).all()
    bar = ProgressBar(total=len(docs))
    for doc in docs:
        t1 = set(doc.tags.split(",")) & all_key
        if t1:
            doc.tags = ",".join(t1)
        else:
            doc.tags = ""
        bar.move()
    db.session.commit()


def soft_delete(ids=[]):
    if not ids:
        offline_ids = set([item.doc_id for item in Docs.query.filter(not Docs.status)])
    else:
        offline_ids = set(ids)
    for item in Grade.query.all():
        docs = item.get_docs() - offline_ids
        item.docs = ",".join(map(str, docs))
    for item in Genre.query.all():
        docs = item.get_docs() - offline_ids
        item.docs = ",".join(map(str, docs))
    for item in Keywords.query.all():
        docs = item.get_docs() - offline_ids
        item.docs = ",".join(map(str, docs))
    for item in Sugs.query.all():
        same = set(item.get_same()) - offline_ids
        similar = set(item.get_similar()) - offline_ids
        item.same_docs = ",".join(map(str, same))
        item.similar_docs = ",".join(map(str, similar))
    db.session.commit()


if __name__ == '__main__':
    # soft_delete()
    set_status()
    # property_avoid()
    # sug_init()
    # genre_grade_make()
    # content_del()
    # slugging()
    # duplicate()
    # showing()
    pass
