#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import jieba
import heapq
import math
import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))  + "/DATA/doclist_all.txt"

# jieba.load_userdict(path)

target = list(jieba.cut("天天炫斗商城系统详解介绍攻略",cut_all = False))
L2 = []


with open(path,"r") as query:
	table = query.readlines()
	contain = []
	shows = [x-x for x in range(len(target))]

	for ii in range(len(table)):
		L1 = table[ii]
		for jj in range(len(target)):
			shows[jj] += L1.count(target[jj])
			

	for k in range(len(target)):
		shows[k] = math.log(len(table)/shows[k])
		if k < 3:
			shows[k] += 3

	for i in range(len(table)):
		L1 = table[i]
		L2.append(L1)
		contain.append(0)
		for j in range(len(target)):
			contain[i] += L1.count(target[j]) * shows[j]/len(target)

print(target)
print(shows)


hahahah = list(map(lambda x,y:[x,y], L2,contain))
	
def sec(t):
	return t[1]

for_print = heapq.nlargest(10, hahahah, key= sec)

print("天天炫斗布雷泽仓木熏布鲁三大职业对比分析攻略")
for xxx in for_print[:10]:
	print(xxx)