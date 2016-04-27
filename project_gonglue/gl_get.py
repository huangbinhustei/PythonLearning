import requests
from pyquery import PyQuery as pq
import time
from random import uniform
import os
import threading
import re
import sqlite3
import json

post = {}
url_list = []


def c_escape(nc_str):
    nc_str.replace("\\", "\\\\")
    nc_str.replace("\"", "\\\"")
    nc_str.replace("\n", "\\\n")
    return nc_str


def database_create():
    connect = sqlite3.connect("chuapp.db")
    cursor = connect.cursor()
    flag = True

    try:
        cursor.execute(
            'create table zhenhaowan ('
            'doc_id integer(200),'
            'doc_former_url varchar(200),'
            'doc_title text(500),'
            'doc_tag text(100),'
            'doc_icon text(100),'
            'doc_description varchar(200),'
            'doc_summary varchar(200),'
            'doc_content varchar(65536)'
            ')'
        )
    finally:
        cursor.close()
        connect.commit()
        connect.close()
        return flag


def get_view_content(url, idx, refer):
    url_list.append(url)
    view_header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36',
        'Referer': refer
    }
    target = requests.get(url=url, headers=view_header).content.decode("utf-8")
    view_div = pq(target)("div")
    post[idx]["summary"] = pq(pq(view_div)(".review-excerpt")).html().replace(u'\xa0', u' ')
    post[idx]["cont"] = pq(pq(view_div)(".the-content.fn-clear")).html().replace(u'\xa0', u' ')
    post[idx]["cont"] = post[idx]["cont"].split("\n")

    sql_statement = "insert into zhenhaowan" \
                    + " (doc_id, " \
                    + " doc_former_url, " \
                    + " doc_title, " \
                    + " doc_tag, " \
                    + " doc_icon, " \
                    + " doc_description, " \
                    + " doc_summary, " \
                    + " doc_cont)" \
                    + "values (" \
                    + str(idx) \
                    + ",\"" + str(url) + "\"" \
                    + ",\"" + str(post[idx]["title"]) + "\"" \
                    + ",\"" + str(post[idx]["tag_png"]) + "\"" \
                    + ",\"" + str(post[idx]["icon"]) + "\"" \
                    + ",\"" + str(post[idx]["description"]) + "\"" \
                    + ",\"" + str(post[idx]["summary"]) + "\"" \
                    + ",\"" + c_escape(",".join(post[idx]["cont"])) + "\")"

    # print(sql_statement)
    print("\n".join(post[idx]["cont"]))

    connect = sqlite3.connect("chuapp.db")
    cursor = connect.cursor()

    try:
        cursor.execute(sql_statement)
    finally:
        cursor.close()
        connect.commit()
        connect.close()


def get_view_url(url_head, page_number=0):
    """
    :param url_head:    待抓取的url头部
    :param page_number: 页码
    :return:            post地址
    """

    if page_number == 0:
        this_url = url_head
    else:
        this_url = url_head + "/page/" + str(page_number)

    target = requests.get(url=this_url, headers=gl_header).content.decode("utf-8")
    post_html = pq(pq(target)("div"))(".content-main-discuss.post")
    print(len(post_html))
    par = re.compile(r'http://www.chuapp.com/\d{4}/\d{2}/\d{2}/(\d+)\.html')
    for item in post_html:
        temp_post_a = pq(item)("a")
        t_url = pq(temp_post_a).attr("href")

        if t_url not in url_list:
            print(t_url)
            idx = re.sub(par, r'\1', t_url)
            post[idx] = {}
            post[idx]["url"] = t_url
            post[idx]["title"] = pq(temp_post_a).attr("title")
            post[idx]["tag_png"] = pq(pq(pq(temp_post_a)("div"))("img")).attr("src")
            post[idx]["icon"] = pq(pq(pq(temp_post_a)("img")))(".fn-left").attr("src")
            post[idx]["description"] = pq(pq(pq(pq(temp_post_a)("ul")))("li"))(".li-description").text()

            get_view_content(t_url, idx, this_url)
            break

            # print(json.dumps(post, ensure_ascii=False))


if __name__ == "__main__":
    gl_header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36',
        'Referer': 'http://www.chuapp.com/category/pcz',
    }
    # database_create()
    start_url = "http://www.chuapp.com/category/pcz"
    get_view_url(start_url, page_number=0)
