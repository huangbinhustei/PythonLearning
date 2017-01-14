#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import threading
import os
import time
import re

a = time.time()
same_time = 10
block_length = 1000
path = os.path.abspath('.')
par = re.compile(r'[a-z]+')

key_file_name = "keys.txt"
result_file_name = "result.txt"
record_file_name = "record.txt"
xml_file_name = "in_xml.txt"


def loading():
    with open(os.path.join(path, xml_file_name), "r", encoding="utf-8") as fx:
        l_keys_in_xml = set([item.strip().lower() for item in fx.readlines()])
    with open(os.path.join(path, key_file_name), "r", encoding="utf-8") as fk:
        l_need_check_title = [item.strip().lower() for item in fk.readlines()]
    with open(os.path.join(path, record_file_name), "r", encoding="utf-8") as fi:
        l_records = [item.strip().split("\t") for item in fi.readlines()]

    with open(os.path.join(path, result_file_name), "w", encoding="utf-8") as fi:
        fi.write(str(time.ctime())+"\n\n")

    return l_keys_in_xml, l_need_check_title, l_records


def soft_check(keys_new, keys_has_checked_before, t_records):
    print(str(len(keys_new)) + ":\tkeys count that need check")
    need_check = []
    keys_has_checked_before = keys_has_checked_before | set([item[0] for item in t_records])
    for item in [title for title in keys_new if title not in keys_has_checked_before]:
        if len(item) < 3 or "www" in item or "com" in item:
            continue
        if len(re.sub(par, "", item)) < len(item):
            continue
        if item.replace("作文", "").replace(" ", "").replace(",", "").replace("，", "") in keys_has_checked_before:
            continue
        need_check.append(item)
    print(str(len(need_check)) + ":\tkeys count that need check after soft_check")
    return need_check


def ald(query_list_small):
    with open(os.path.join(path, result_file_name), "a") as fi:
        with open(os.path.join(path, record_file_name), "a", encoding="utf-8") as f2:
            for s_1 in query_list_small:
                s = s_1.strip()
                r = requests.get("https://m.baidu.com/s?word=" + s)
                if 200 != r.status_code:
                    fi.write(s + "\t打开失败\n")
                    continue
                c = r.content.decode("utf-8")
                if "gonglvezuowen" in c:
                    fi.write(s + "\t有阿拉丁\n")
                    f2.write(s + "\t有阿拉丁\n")
                    continue
                if "wise_zuowen_mini" in c:
                    fi.write(s + "\t有阿拉丁\n")
                    f2.write(s + "\t有阿拉丁\n")
                    continue
                fi.write(s + "\t无阿拉丁\n")
                f2.write(s + "\t无阿拉丁\n")


if __name__ == '__main__':
    keys_in_xml, need_check_title, records = loading()
    # need_check_title = soft_check(need_check_title, keys_in_xml, records)
    block_count = 0
    while 1:
        block = need_check_title[block_count * block_length: (block_count + 1) * block_length]
        print(str(block_count * block_length))
        block_count += 1
        if len(block) == 0:
            break
        th = []
        for i in range(same_time):
            th.append(threading.Thread(target=ald, args=(block[i::same_time],)))
        for t in th:
            t.setDaemon(True)
            t.start()
        for t in th:
            t.join()
