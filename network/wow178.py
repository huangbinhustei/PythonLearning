# -*- coding: utf-8 -*-

import requests
from collections import defaultdict
import re
import time
from pyquery import PyQuery as pq
import os

me_try = [
	"http://wow.178.com/list/dh/index",
	"http://wow.178.com/list/sm/index",
	"http://wow.178.com/list/dk/index",
	"http://wow.178.com/list/sq/index",
	"http://wow.178.com/list/dly/index",
	"http://wow.178.com/list/dz/index",
	"http://wow.178.com/list/ws/index",
	"http://wow.178.com/list/zs/index",
	"http://wow.178.com/list/lr/index",
	"http://wow.178.com/list/fs/index",
	"http://wow.178.com/list/ms/index",
	"http://wow.178.com/list/ss/index",
	"http://wow.178.com/list/zhiye/index",
	"http://wow.178.com/all/index",
	"http://wow.178.com/list/syjn/index",
	"http://wow.178.com/list/166839750840",
	"http://wow.178.com/list/18492166368",
	"http://wow.178.com/list/yuanchuang/index",
	"http://wow.178.com/list/zhuangbei/index",
	"http://wow.178.com/list/241325916206",
	"http://wow.178.com/list/wupin/index",
	"http://wow.178.com/list/232880924170",
	"http://wow.178.com/list/fuben/index",
	"http://wow.178.com/list/pvp/index",
	"http://wow.178.com/list/18491924437",
	"http://wow.178.com/list/blue/index",
	"http://wow.178.com/list/75948938370",
	"http://wow.178.com/list/193257209153",
	"http://wow.178.com/list/232857559261",
	"http://wow.178.com/list/116740816675",
	"http://wow.178.com/list/222985549910",
	"http://wow.178.com/list/222987333864",
	"http://wow.178.com/list/200616152944",
	"http://wow.178.com/list/133399052144",
	"http://wow.178.com/list/200616165870",
	"http://wow.178.com/list/199504361634",
	"http://wow.178.com/list/caoyao/index",
	"http://wow.178.com/list/18492416624",
	"http://wow.178.com/list/gongcheng/index",
	"http://wow.178.com/list/78777215178",
	"http://wow.178.com/list/fumo/index",
	"http://wow.178.com/list/zhubao/index",
	"http://wow.178.com/list/mingwen/index",
	"http://wow.178.com/list/duanzao/index",
	"http://wow.178.com/list/zhipi/index",
	"http://wow.178.com/list/caifeng/index",
	"http://wow.178.com/list/lianjin/index",
	"http://wow.178.com/list/diaoyu/index",
	"http://wow.178.com/list/pengren/index",
	"http://wow.178.com/list/caikuang/index",
	"http://wow.178.com/list/18492451452"
]


def get_content(this_target_url):
    final = []

    this_target = requests.get(this_target_url).content.decode("utf-8")
    this_target = pq(pq(this_target)(".list20"))(".txt")

    for item in this_target:
        temp_title = pq(pq(item)("h5")).text()
        temp_title = temp_title.replace("\t"," ")
        temp_url = pq(pq(item)("a")).attr("href")
        temp_data = pq(pq(item)("p"))(".t01").text()
        temp_data = re.sub(r'.+时间', "", temp_data,flags=re.S)[1:]
        final.append(temp_title + "\t" + temp_url + "\t" + temp_data)

    return final

if __name__ == '__main__':
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/result_game/wow.txt"
    for list_item in me_try:
        page_number = 1

        while 1:
            target_url = list_item + "_" + str(page_number) + ".html"
            if page_number == 1:
                target_url = list_item + ".html"
            time.sleep(0.2)

            try:
                get_list = get_content(target_url)
                if not get_list:
                    break
                print(target_url)
                with open(path, "a") as f:
                    for item in get_list:
                        f.write(str(item) + "\n")

                page_number += 1
            except Exception as e:
                break
