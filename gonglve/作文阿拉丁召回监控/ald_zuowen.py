#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import threading
import os
import time

a = time.time()
same_time = 10
path = os.path.abspath('.')

key_file_name = "keys.txt"
result_file_name = "result.txt"


def ald(query_list_small):
    with open(os.path.join(path, result_file_name), "a") as fi:
        for s_1 in query_list_small:
            s = s_1.strip()
            r = requests.get("https://m.baidu.com/s?word=" + s)
            if 200 != r.status_code:
                fi.write(s + "\t打开失败\n")
                continue
            c = r.content.decode("utf-8")
            if "gonglvezuowen" in c:
                fi.write(s + "\t有阿拉丁\n")
                continue   
            if "wise_zuowen_mini" in c:
                fi.write(s + "\t有阿拉丁\n")
                continue
            fi.write(s + "\t无阿拉丁\n")


if __name__ == '__main__':
    with open(os.path.join(path, key_file_name), "r") as f:
        all_title = f.readlines()
    with open(os.path.join(path, result_file_name), "w") as fi:
        fi.write(str(time.ctime())+"\n\n")

    th = []
    for i in range(same_time):
        th.append(threading.Thread(target=ald, args=(all_title[i::same_time],)))
    for t in th:
        t.setDaemon(True)
        t.start()
    for t in th:
        t.join()
