#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from pyquery import PyQuery as pq
from data import Docs, db
from sqlalchemy import desc
import time

for item in Docs.query.order_by(desc(Docs.create_time)).limit(10):
    print(item.title + "\t" + item.grade + "\t" + str(item.words) + "1")
    print(item.title + "\t" + item.grade + "\t" + "1")
    break