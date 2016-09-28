#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from pyquery import PyQuery as pq
import time
import sys

with open("/Users/baidu/Downloads/439.txt", "r") as f:
	all_title = f.readlines()
tot = len(all_title)

def ald(s,fi):
	r = requests.get("https://m.baidu.com/s?word=" + s)

	if 200 != r.status_code:
		fi.write(s+"\t打开失败\n")
		return
	c=r.content
	for t in pq(c)(".c-span6"):
		if "百度文库·作文" in pq(t).text():
			fi.write(s+"\t有阿拉丁\n")
			return
	fi.write(s+"\t无阿拉丁\n")


i = 0
for item in all_title:
	with open("/Users/baidu/Documents/百度/Git/PythonLearning/gonglve/作文query及结果.txt", "a") as f:
		ald(item.strip(), f)
		i += 1
		sys.stdout.write(str(i) + "/" + str(tot) +"\r")
		sys.stdout.flush()
