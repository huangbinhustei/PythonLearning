#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from data import Docs, db
from sqlalchemy import desc

done = [item.doc_md for item in Docs.query.all()]
done1 = [item.doc_md for item in Docs.query.order_by(desc(Docs.create_time)).all()]

print(str(len(done)) + str(len(done)/20))
print(done[1])