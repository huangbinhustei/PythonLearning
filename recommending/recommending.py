#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import xlrd
import jieba
import heapq
import math
import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))  + "/DATA/doclistmini.xlsx"

# jieba.load_userdict(path)

target = list(jieba.cut("天天炫斗布雷泽仓木熏布鲁三大职业对比分析攻略",cut_all = False))
# target = ["天天炫斗","布雷泽","仓木熏","布鲁","三","大","职业","对比","分析"]
L2 = []

with xlrd.open_workbook(path) as query:
	table = query.sheets()[0] 
	contain = []
	shows = [x-x for x in range(len(target))]

	for ii in range(table.nrows):
		L1 =table.cell(ii,0).value
		for jj in range(len(target)):
			shows[jj] += L1.count(target[jj])

	for k in range(len(target)):
		shows[k] = math.log(table.nrows/shows[k])

	for i in range(table.nrows):
		L1 =table.cell(i,0).value
		L2.append(L1)
		contain.append(0)
		for j in range(len(target)):
#			if L1.count(target[j]) >0 :
#				contain[i] += shows[j]

			contain[i] += L1.count(target[j]) * shows[j]

print(target)
print(shows)


hahahah = list(map(lambda x,y:[x,y], L2,contain))
	
def sec(t):
	return t[1]

for_print = heapq.nlargest(10, hahahah, key= sec)

print(for_print[:10])