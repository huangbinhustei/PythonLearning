import requests
import threading
import os
from pyquery import PyQuery as pq
import time
import sys

a = time.time()
same_time = 10
path = os.path.abspath('.')


def ald(s):
    with open(os.path.join(path, "作文query及结果.txt"), "a") as fi:
        r = requests.get("https://m.baidu.com/s?word=" + s)
        if 200 != r.status_code:
            fi.write(s + "\t打开失败\n")
            return
        c = r.content.decode("utf-8")
        if "gonglvezuowen" in c:
            fi.write(s + "\t有阿拉丁\n")
            return   
        if "wise_zuowen_mini" in c:
            fi.write(s + "\t有阿拉丁\n")
            return
        fi.write(s + "\t无阿拉丁\n")
        return


def make_th(query_list_small):
    th = []
    for q in query_list_small:
        th.append(threading.Thread(target=ald, args=(q.strip(),)))
    for t in th:
        t.setDaemon(True)
        t.start()
    for t in th:
        t.join()


def void_main():
    with open(os.path.join(path, "keys.txt"), "r") as f:
        all_title = f.readlines()
        tot = len(all_title)
    with open(os.path.join(path, "作文query及结果.txt"), "w") as fi:
        fi.write(str(time.ctime())+"\n\n")
    i=0
    while 1:
        temp = all_title[i * same_time : (i+1) * same_time]
        if not temp:
            break

        make_th(temp)
        i += 1
        sys.stdout.write(str(i*10+len(temp)-10) + "/" + str(tot) +"\r")
        sys.stdout.flush()

void_main()