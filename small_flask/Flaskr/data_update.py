# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from header_flaskr import Docs, Tags, db, app
import jieba
import jieba.analyse
import html
from collections import defaultdict


def tag_init():
    for post in Docs.query.all():
        content = pq(html.unescape(post.text)).text()
        if len(content) > 500:
            post.tag = ",".join(jieba.analyse.extract_tags(content, topK=5, withWeight=False))
        else:
            post.tag = ""
        db.session.add(post)

    db.session.commit()


def tag_tab_make():
    tags_dict = defaultdict(lambda: [])

    for post in Docs.query.all():
        for tag in str(post.tag).split(","):
            tags_dict[tag].append(str(post.id))

    for tag, ids in tags_dict.items():
        if len(ids) > 8:
            new_tag = Tags([tag, ",".join(ids)])
            db.session.add(new_tag)

    db.session.commit()

if __name__ == '__main__':
    tag_init()
    tag_tab_make()
