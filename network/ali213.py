# -*- coding: utf-8 -*-

import requests
from collections import defaultdict
import re
import time
from pyquery import PyQuery as pq
import os

gl_content = defaultdict(lambda: 0)
key_tuple = ("title", "keywords", "description", "game_name", "game_id", "source_url", "author", "doc_title", "content")

me_try = [
    # ["变形金刚：毁灭", "http://gl.ali213.net/html/2015-10/86933"],
    # ["彩虹六号：围攻", "http://gl.ali213.net/html/2015-12/95215"],
    # ["恶灵附身", "http://gl.ali213.net/html/2014-10/50191"],
    # ["方舟：生存进化", "http://gl.ali213.net/html/2015-6/69805"],
    # ["辐射4", "http://gl.ali213.net/html/2015-11/91753"],
    # ["古墓丽影：崛起", "http://gl.ali213.net/html/2015-11/91031"],
    # ["合金装备5：幻痛", "http://gl.ali213.net/html/2015-9/81963"],
    # ["龙之信条：黑暗崛起", "http://gl.ali213.net/html/2016-1/102239"],
    # ["三国志13", "http://gl.ali213.net/html/2016-1/105399"],
    # ["生化危机0高清版", "http://gl.ali213.net/html/2016-1/104039"],
    # ["使命召唤12：黑色行动3", "http://gl.ali213.net/html/2015-11/91245"],
    # ["巫师3：狂猎", "http://gl.ali213.net/html/2015-5/68823"],
    # ["侠客风云传", "http://gl.ali213.net/html/2015-7/76033"],
    # ["伊苏：树海", "http://gl.ali213.net/html/2015-10/89997"],
    # ["勇者斗恶龙：英雄", "http://gl.ali213.net/html/2015-12/95807"],
    # ["正当防卫3", "http://gl.ali213.net/html/2015-12/95217"],
    # ["GTA5（侠盗猎车手5）", "http://gl.ali213.net/html/2015-4/65525"],
    ["刺客信条：枭雄", "http://gl.ali213.net/html/2015-11/90629"],
    ["刺客信条4：黑旗", "http://gl.ali213.net/html/2014-6/42484"],
    ["刺客信条：大革命", "http://gl.ali213.net/html/2014-11/53997"],
    ["刺客信条：兄弟会", "http://gl.ali213.net/html/2014-6/42505"],
    ["刺客信条：叛变", "http://gl.ali213.net/html/2014-11/53675"],
    ["刺客信条：启示录", "http://gl.ali213.net/html/2014-6/42610"],
    ["火影忍者：究极忍者风暴4", "http://gl.ali213.net/html/2015-8/77655"],
    ["孤岛惊魂4", "http://gl.ali213.net/html/2014-11/54427"],
    ["消逝的光芒", "http://gl.ali213.net/html/2015-1/60303"],
    ["最终幻想13：雷霆归来", "http://gl.ali213.net/html/2015-12/96889"],
    ["圣斗士星矢：战士魂", "http://gl.ali213.net/html/2015-12/95307"]
]

init_dict = {
    "url_head": "http://gl.ali213.net/html/2016-1/104039",
    "game_name": "生化危机0高清版",
}


def get_content(this_target_url):
    this_target = requests.get(this_target_url).content.decode("utf-8")
    # 固定内容
    gl_content["source_url"] = this_target_url
    gl_content["author"] = "ali213"
    gl_content["game_name"] = init_dict["game_name"]
    gl_content["game_id"] = "-1"

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
        if pq(item1).text().find("游戏专题：http://www.ali213") == 0:
            continue
        if pq(item1).text() == "N/A":
            continue
        if pq(item1).text().find("作者") == 0 or pq(item1).text().find("来源") == 0 or pq(item1).text().find("欢迎转载") == 0:
            continue
        temp.append(pq(item1).text())
    gl_content["content"] = temp

    # 文档标题
    p_ye_ma = re.compile(r'.+_')
    ye_ma = re.sub(p_ye_ma, "", this_target_url).replace(".html", "")
    if len(ye_ma) > 3:
        ye_ma = "1"
    x = pq(this_target)("h1").text()
    gl_content["doc_title"] = x + "(" + ye_ma + ")"


if __name__ == '__main__':
    for game_item in me_try:
        init_dict["game_name"] = game_item[0]
        init_dict["url_head"] = game_item[1]
        url_head = game_item[1]

        path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/result_game/" + str(
            game_item[0]) + ".txt"

        page_number = 1
        with open(path, "w") as begin:
            begin.write("{\n\t" + r'"list": [{' + "\n")

        while 1:
            target_url = url_head + "_" + str(page_number) + ".html"
            if page_number == 1:
                target_url = url_head + ".html"
            print(target_url)
            time.sleep(0.4)

            try:
                get_content(target_url)
                with open(path, "a") as f:
                    if page_number > 1:
                        f.write("\t\t]\n\t},{\n")
                    f.write("\t\t" + r'"page_number": "' + str(page_number) + r'",' + "\n")
                    for item in key_tuple:
                        if item == "content":
                            row_of_content = gl_content["content"]
                            f.write("\t\t" + r'"content": [' + "\n")
                            for row in row_of_content:
                                f.write("\t\t\t" + r'"' + str(row) + r'",' + "\n")
                        else:
                            f.write("\t\t" + r'"' + str(item) + r'": "' + str(gl_content[item]) + r'",' + "\n")
                page_number += 1
            except Exception as e:
                with open(path, "a") as f:
                    f.write("\t\t]\n\t}]\n}")
                break
