#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from data import Docs, db, cost_count
from sqlalchemy import desc, or_
from collections import defaultdict
from slugify import UniqueSlugify
import re, os


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
def counting():
    print("counting begin")
    done = [item.doc_md for item in Docs.query.order_by(desc(Docs.create_time)).all()]
    print(str(len(done)) + "\t" + str(len(set(done))) + "\t" + str(int(len(done) / 20)))


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
def showing():
    lines = [item for item in Docs.query.limit(10)]
    print("\n".join(line.title for line in lines))


@cost_count
def former_url_update():
    print("11")
    Docs.query.filter(Docs.doc_md == "2a4563b80066f5335b812131").update({"view": 1})
    db.session.commit()


@cost_count
def property_avoid():
    par = re.compile(r'''<p>[^/]+?年级[：:].+?</p>''')
    print("property_avoid begin")
    # f = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "temp.txt"), "w", encoding="utf-8")
    throw = ("<p>", "</p>", ":", "：")
    comp_with_property = [item for item in
                          Docs.query.filter(or_(Docs.content.like("%年级：%"), Docs.content.like("%年级:%")))]
    for item in comp_with_property:
        danger_part = ",".join(re.findall(par, item.content))
        writer_1 = danger_part.split("年级:")[-1].replace("</p>", "").strip()
        writer_2 = danger_part.split("年级：")[-1].replace("</p>", "").strip()
        writer = writer_1 if len(writer_1) < len(writer_2) else writer_2
        orgs = danger_part.replace(writer, "")
        for p in throw:
            orgs = orgs.replace(p, "")
        orgs = orgs.strip().replace("\t", "")

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

        flag = False
        if ((len(danger_part) - len(writer) - len(orgs)) < 10) and (10 > len(writer) > 0):
            if orgs[:2] in province:
                if len(orgs) < 50:
                    flag = True
            else:
                if len(orgs) < 20:
                    flag = True
        # flag = True
        if flag:
            item.author = writer
            item.former_org = orgs
            item.content = item.content.replace(danger_part2, "")
            # print(item.doc_md + "\t" + writer + "\t" + orgs + "\t" + danger_part, file=f)
    db.session.commit()
    # f.close()
    print(len(comp_with_property))


@cost_count
def content_del():
    print("content_del begin")
    # f = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "temp.txt"), "w", encoding="utf-8")
    par_1 = re.compile("<p>[　 \t]+")
    par_2 = re.compile("[ 　\t]+</p>")
    need_del = {"%<p> %", "%<p>　%", "%<p>	%"}
    for par in need_del:
        for item in Docs.query.filter(Docs.content.like(par)):
            # print(item.content, file=f)
            temp = re.sub(par_1, "<p>", item.content)
            temp = re.sub(par_2, "</p>", temp)
            item.content = temp
            # print(temp, file=f)
            # print("\n\n", file=f)
        print("culc end")
        db.session.commit()
    # f.close()


if __name__ == '__main__':
    pass
    # content_del()
    # slugging()
    # duplicate()
    # showing()
