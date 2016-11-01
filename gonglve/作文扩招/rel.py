#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests as req
from pyquery import PyQuery as pq
import time

u = "http://gl.baidu.com/zuowen/search/composition?keywords="

nun = ["的","关于","00","作文","00字","1","2","3","4","5","6","7","8","初","初中","高","高中","小","小学","年级","一","二","三","四","五","六","七","八","九","十"]

with open("/Users/baidu/Documents/百度/Git/PythonLearning/gonglve/作文扩招/final_2.txt","r") as f:
	titles = f.readlines()

for t in titles:
	temp = t.split(",")
	query = temp[0].strip()
	url = u + query
	print(url)
	r = req.get(url)
	time.sleep(0.2)
	print(r.status_code)
	x = pq(pq(r.content)("ul")(".doc-list")("div")(".title.text-blue.flex-one")[0]).text()

	temp_query = query
	for xxx in nun:
		temp_query = temp_query.replace(xxx,"")
	cou = 0
	for k in temp_query:
		if k in x:
			cou +=1
	if len(temp_query) == 0:
		cou = 2
	else:
		cou = cou/len(temp_query)
	with open("/Users/baidu/Documents/百度/Git/PythonLearning/gonglve/作文扩招/res.txt","a") as f:
		f.write(query + "\t" + x.strip().replace(" ","")+ "\t" + str(cou)[:5] +"\n")