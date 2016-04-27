# -*- coding: utf-8 -*-

import requests
from collections import defaultdict
import re
import time
from pyquery import PyQuery as pq
import os
import json
import logging

logging.basicConfig(level=logging.INFO)
gl_content = defaultdict(lambda: 0)
path = os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/"
key_tuple = ("title", "keywords", "description", "game_name", "game_id", "source_url", "author", "doc_title", "content")

game_target = [
    # ["巫师3", "http://gl.ali213.net/html/2015-5/68823", 1766],
    # ["辐射4", "http://gl.ali213.net/html/2015-11/91753", 10681],
    # ["GTA5（侠盗猎车手5）", "http://gl.ali213.net/html/2015-4/65525", 11018],
    ["变形金刚：毁灭", "http://gl.ali213.net/html/2015-10/86933", 30165],
    # ["彩虹六号：围攻", "http://gl.ali213.net/html/2015-12/95215", 30166],
    # ["恶灵附身", "http://gl.ali213.net/html/2014-10/50191", 30167],
    # ["方舟：生存进化", "http://gl.ali213.net/html/2015-6/69805", 30168],
    # ["古墓丽影：崛起", "http://gl.ali213.net/html/2015-11/91031", 30169],
    # ["合金装备5：幻痛", "http://gl.ali213.net/html/2015-9/81963", 30170],
    # ["龙之信条：黑暗崛起", "http://gl.ali213.net/html/2016-1/102239", 30171],
    # ["三国志13", "http://gl.ali213.net/html/2016-1/105399", 30172],
    # ["生化危机0高清版", "http://gl.ali213.net/html/2016-1/104039", 30173],
    # ["使命召唤12：黑色行动3", "http://gl.ali213.net/html/2015-11/91245", 30174],
    # ["侠客风云传", "http://gl.ali213.net/html/2015-7/76033", 30175],
    # ["伊苏：树海", "http://gl.ali213.net/html/2015-10/89997", 30176],
    # ["勇者斗恶龙：英雄", "http://gl.ali213.net/html/2015-12/95807", 30177],
    # ["正当防卫3", "http://gl.ali213.net/html/2015-12/95217", 30178],
    # ["刺客信条：枭雄", "http://gl.ali213.net/html/2015-11/90629", 30179],
    # ["刺客信条4：黑旗", "http://gl.ali213.net/html/2014-6/42484", 30180],
    # ["刺客信条：大革命", "http://gl.ali213.net/html/2014-11/53997", 30181],
    # ["刺客信条：兄弟会", "http://gl.ali213.net/html/2014-6/42505", 30182],
    # ["刺客信条：叛变", "http://gl.ali213.net/html/2014-11/53675", 30183],
    # ["刺客信条：启示录", "http://gl.ali213.net/html/2014-6/42610", 30184],
    # ["火影忍者：究极忍者风暴4", "http://gl.ali213.net/html/2015-8/77655", 30185],
    # ["孤岛惊魂4", "http://gl.ali213.net/html/2014-11/54427", 30186],
    # ["消逝的光芒", "http://gl.ali213.net/html/2015-1/60303", 30187],
    # ["最终幻想13：雷霆归来", "http://gl.ali213.net/html/2015-12/96889", 30188],
    # ["圣斗士星矢：战士魂", "http://gl.ali213.net/html/2015-12/95307", 30189]
]

init_dict = {}

par = re.compile(r'> +')
par_more = (
    re.compile(r'<p>更多相关资讯.+'),
    re.compile(r'<p></p>'),
    re.compile(r'<p>游戏专题[^<]+'),
    re.compile(r'<p>[^>]+213[^<]+</p>'))
par_need_del = ("\n", "\r", "　", "&#13;", "【游侠攻略组】")


def html_format(unformed_str):
    temp = unformed_str.replace("\\", "\\\\")
    for item in par_need_del:
        temp = temp.replace(item, "")
    temp = re.sub(par, '>', temp)
    return temp.replace(r'"', r'\"').strip()


def get_content(this_target_url, local_page_number):
    this_target = requests.get(this_target_url).content.decode("utf-8")

    # 页面描述信息
    title = pq(pq(this_target)("title")).text().replace("_游侠网", "")
    meta = pq(this_target)("meta")
    for item1 in meta:
        if pq(item1).attr("name") == "keywords":
            keywords = pq(item1).attr("content")
        if pq(item1).attr("name") == "description":
            description = pq(item1).attr("content")

    # 页面内容
    content_html = pq(pq(this_target)("div"))(".glzjshow_con")
    temp = pq(content_html).html()
    temp = html_format(temp)
    for par_item in par_more:
        temp = re.sub(par_item, '', temp)

    gl_content_single_page = {
        "source_url": this_target_url,
        "author": "ali213",
        "game_name": init_dict["game_name"],
        "game_id": init_dict["game_id"],

        "title": html_format(title),
        "keywords": html_format(keywords),
        "description": html_format(description),

        "content": temp
    }

    gl_content[str(local_page_number)] = gl_content_single_page
    logging.debug(gl_content)
    logging.debug("\n\n")


if __name__ == '__main__':
    for game in game_target:
        init_dict["game_name"] = game[0]
        init_dict["url_head"] = game[1]
        init_dict["game_id"] = str(game[2])
        path = path + init_dict["game_name"] + ".txt"
        page_number = 1

        while 1:
            target_url = init_dict["url_head"] + "_" + str(page_number) + ".html"
            if page_number == 1:
                target_url = init_dict["url_head"] + ".html"
                print(target_url)
            time.sleep(0.4)

            try:
                get_content(target_url, page_number)
                page_number += 1
            except Exception as e:
                logging.info(str(e))
                break

            # if page_number == 3:
            #     break

        with open(path, "a") as f:
            f.write(json.dumps(gl_content, ensure_ascii=False, indent=4))
            f.write("\n\n")
