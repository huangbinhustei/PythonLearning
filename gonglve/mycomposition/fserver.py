#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from data import Docs, db
from sqlalchemy import desc
from collections import defaultdict
import time

t = time.time


def counting():
    print("counting begin")
    done = [item.doc_md for item in Docs.query.order_by(desc(Docs.create_time)).all()]
    print(str(len(done)) + "\t" + str(len(set(done))) + "\t" + str(int(len(done)/20)))


def duplicate():
    a = t()
    print("duplicating begin")
    dict_lines = defaultdict(lambda: [])
    lines = [item for item in Docs.query.order_by(desc(Docs.create_time)).all()]
    print(str(t()-a)[:5] + "s\tload completed")
    for line in lines:
        dict_lines[line.doc_md].append(line)
    print(str(t()-a)[:5] + "s\tinto dict done")
    thing_to_del = []
    for k, v in dict_lines.items():
        if len(v) > 1:
            for item in v[1:]:
                thing_to_del.append(item)
    print(str(len(thing_to_del)) + "rows need del")
    for item in thing_to_del:
        db.session.delete(item)
    db.session.commit()
    print(str(t()-a)[:5] + "s\tthings has done")


def showing():
    a = t()
    lines = [item for item in Docs.query.limit(10)]
    print("\n".join(line.title for line in lines))
    print(t()-a)

if __name__ == '__main__':
    # counting()
    duplicate()
    # showing()
