#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from data import Docs, db
from sqlalchemy import desc

i=0
for item in Docs.query.order_by(desc(Docs.create_time)).all():
    print(item.title + "\t" + item.grade + "\t" + str(item.words))
    i+=1
print(str(i))