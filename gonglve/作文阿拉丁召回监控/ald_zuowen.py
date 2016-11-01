#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from pyquery import PyQuery as pq
import time
import sys
import os

path = os.path.abspath('.')

with open(os.path.join(path, "keys.txt"), "r") as f:
	all_title = f.readlines()
tot = len(all_title)

def ald(s,fi):
	r = requests.get("https://m.baidu.com/s?word=" + s)

	if 200 != r.status_code:
		fi.write(s+"\t打开失败\n")
		return
	c=r.content
	for t in pq(c)(".c-span6"):
		if "百度文库·作文" in pq(t).text() or "wise_zuowen_mini" in c.decode("utf-8"):
			fi.write(s+"\t有阿拉丁\n")
			return


i = 0
for item in all_title:
	with open(os.path.join(path, "作文query及结果.txt"), "a") as f:
		ald(item.strip(), f)
		i += 1
		sys.stdout.write(str(i) + "/" + str(tot) +"\r")
		sys.stdout.flush()
