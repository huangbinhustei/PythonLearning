# -*- coding: utf-8 -*-
import requests
from pyquery import PyQuery as pq
import time
import os
import re
from random import uniform
import sqlite3


def database_create():
    connect = sqlite3.connect("novel.db")
    cursor = connect.cursor()
    flag = True

    try:
        cursor.execute(
                'create table the_door'
                '(key_chapter int primary key,title varchar(100),content varchar(10000))'
        )
    except Exception as e:
        print("error: " + str(e) + " @ database_create")
        flag = False
    finally:
        cursor.close()
        connect.commit()
        connect.close()
        return flag


def save_content():
    url = "http://www.88xiaoshuo.com/Partlist/47317/Index.shtml"
    target = requests.get(url).content
    dd_list = pq(pq(target)("div"))("dd")

    dd_url_list = []
    i = 0
    chapter = 0
    url_list_done = set([])

    for item in dd_list:
        if pq(item).text()[0] == "第":
            dd_url_list.append(pq(pq(item)("a")).attr("href"))

    for item in dd_url_list:
        if i < 500:
            i += 1
            continue
        this_url = "http://www.88xiaoshuo.com/Partlist/47317/" + item
        if this_url in url_list_done:
            print("重复了")
            continue
        url_list_done.add(this_url)
        print(str(time.ctime()) + "  " + this_url)
        connect = sqlite3.connect("novel.db")
        cursor = connect.cursor()
        try:
            lm = requests.get(this_url).content
            tit = pq(pq(lm)("title")).text()
            print(tit)
            txt = pq(pq(lm)(".zhangjieTXT")).text()
            cursor.execute('insert into the_door(key_chapter,title,content) values (?,?,?)', (chapter, tit, txt))
            chapter += 1
        except Exception as e:
            print(e)
            pass
        finally:
            time.sleep(uniform(0.2, 1))
            cursor.close()
            connect.commit()
            connect.close()


if __name__ == '__main__':
    database_create()
    save_content()
