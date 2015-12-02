#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import xlrd
import jieba


target = list(jieba.cut("天天炫斗商城系统详解介绍攻略",cut_all = False))
L2 = []

with xlrd.open_workbook("/Users/baidu/微云/project/meijieba/docListall.xlsx") as query:
	table = query.sheets()[0] 
	contain = []
	for i in range(table.nrows):
		L1 =table.cell(i,0).value
		L2.append(L1)
		contain.append(0)
		for tar in target:
			contain[i] += L1.count(tar)
			# contain[i] /= len(target)

hahahah = list(map(lambda x,y:[x,y], L2,contain))
	
def sec(t):
	return t[1]

for_print = sorted(hahahah,key = sec,reverse=True)

print(for_print[:10])