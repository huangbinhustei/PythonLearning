# -*- coding: utf-8 -*-

import requests
from collections import defaultdict
import re
import time
from pyquery import PyQuery as pq
import os

gl_content = defaultdict(lambda: 0)
key_tuple = ("title", "keywords", "description", "game_name", "game_id", "source_url", "author", "doc_title", "content")

init_dict = {
    "url_head": "http://gl.ali213.net/html/2015-11/91245",
    "author": "ali213",
    "game_name": "使命召唤12:黑色行动3",
    "game_id": "-1",
}

path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/result_game/" + str(
        init_dict["game_name"]) + ".txt"


def get_content(this_target):
    # 固定内容
    gl_content["source_url"] = target_url
    gl_content["author"] = init_dict["author"]
    gl_content["game_name"] = init_dict["game_name"]
    gl_content["game_id"] = init_dict["game_id"]

    # 页面描述信息
    title = pq(pq(this_target)("title")).text().replace("_游侠网", "")
    meta = pq(this_target)("meta")
    for item1 in meta:
        if pq(item1).attr("name") == "keywords":
            keywords = pq(item1).attr("content")
        if pq(item1).attr("name") == "description":
            description = pq(item1).attr("content")

    gl_content["title"] = title
    gl_content["keywords"] = keywords
    gl_content["description"] = description

    # 页面内容
    temp = []
    html_p = pq(this_target)("p")
    for item1 in html_p:
        if pq(pq(item1)("img")).attr("src") is not None:
            temp.append(pq(pq(item1)("img")).attr("src"))
            continue
        if pq(item1).text().find("更多相关") == 0 or pq(item1).text().find(">>查看") == 0:
            continue
        temp.append(pq(item1).text())
    gl_content["content"] = temp

    # 文档标题
    ye_ma = re.compile(r'第(\d+)页')
    x = pq(this_target)("h2")
    for item1 in x:
        if pq(item1).text().find("第") == 0:
            gl_content["doc_title"] = "《使命召唤12：黑色行动3》图文全流程攻略 收集品位置+装饰获取" + re.sub(ye_ma, r'(\1)', pq(item1).text())
            break


if __name__ == '__main__':
    url_head = init_dict["url_head"]
    page_number = 1
    with open(path, "w") as begin:
        begin.write("{\n\t" + r'"list": [{' + "\n")

    while 1:
        target_url = url_head + "_" + str(page_number) + ".html"
        if page_number == 1:
            target_url = url_head + ".html"
        print(target_url)
        time.sleep(2)

        try:
            target = requests.get(target_url).content.decode("utf-8")
            get_content(target)
        except Exception as e:
            break
        with open(path, "a") as f:
            f.write("\t\t" + r'"page_number":"' + str(page_number) + r'",' + "\n")
            for item in key_tuple:
                if item == "content":
                    row_of_content = gl_content["content"]
                    f.write("\t\t" + r'"content": [' + "\n")
                    for row in row_of_content:
                        f.write("\t\t\t" + r'"' + str(row) + r'",' + "\n")
                else:
                    f.write("\t\t" + r'"' + str(item) + r'": "' + str(gl_content[item]) + r'",' + "\n")

            f.write("\t\t]\n\t},{\n")
        page_number += 1
