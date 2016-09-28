#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import requests
import sys
import os

path = os.path.abspath('.')
xml_head = "http://cp01-wenku-test2.cp01.baidu.com:8080/static/wenku_aladdin/glyouxi/index/"

new_xml_path = path + "/result_game_xml_manual/99999.xml"
new_titles_path = path + "/result_game_xml_manual/new_titles.txt"

par_desc_fir = re.compile(r'<desc>.+?</desc>')
par_desc_sec = re.compile(r'<abstract>.+?</abstract>')


def special_miracle_nikki(str_before):
    temp = str_before.replace("<key>奇迹暖暖少女级</key><display><url>http://gl.baidu.com/game/12</url>",
                              "<key>奇迹暖暖少女级</key><display><url>http://gl.baidu.com/game/pic/1?level1Id=1</url>")
    str_end = temp.replace("<key>奇迹暖暖公主级</key><display><url>http://gl.baidu.com/game/12</url>",
                           "<key>奇迹暖暖公主级</key><display><url>http://gl.baidu.com/game/pic/2?level1Id=1</url>")
    return str_end


def write_body(game):
    game_name = game["game_name"]
    xml_url = xml_head + game["xml_name"]
    new_keys = game["keys"]

    temp = r'<item><key>' + game_name + r'攻略</key>.+?<item>'
    par_need = re.compile(temp)
    desc = "百度攻略《游戏名》专区每天都有最新的《游戏名》攻略资料发布，提供《游戏名》下载、通关攻略、图文攻略、视频攻略、礼包发放等多种服务..".replace("游戏名", game_name)
    former_xml = requests.get(xml_url).content.decode("utf-8")
    xml_filtered_by_re = re.findall(par_need, former_xml)[0]
    need_xml = xml_filtered_by_re.replace("</item><item>", "</item>")

    if need_xml:
        need_xml = re.sub(par_desc_fir, "<desc>" + desc + "</desc>", need_xml)
        need_xml = re.sub(par_desc_sec, "<abstract>" + desc + "</abstract>", need_xml)

        with open(new_xml_path, "a") as f:
            for key in new_keys:
                for_write = "\t" + need_xml.replace("<key>" + game_name + "攻略</key>", "<key>" + key + "</key>") + "\n"
                if "奇迹暖暖" == game_name:
                    for_write = special_miracle_nikki(for_write)
                f.write(for_write)
    else:
        print("没找到")


def xml_maker(local_conf):
    # xml_header_maker_begin
    with open(new_xml_path, "w") as f:
        f.write(r'<?xml version="1.0" encoding="utf-8"?>' + "\n")
        f.write("<DOCUMENT>\n")
    # xml_header_maker_end

    # xml_body_maker_begin
    i = 0
    task_len = len(local_conf)
    for item in local_conf:
        write_body(item)
        i += 1
        sys.stdout.write(str(i) + "/" + str(task_len) + "\t" + item["game_name"] + "\t\t\t\t\r")
        sys.stdout.flush()
    # xml_body_maker_end

    # xml_foot_maker_begin
    with open(new_xml_path, "a") as f:
        f.write("</DOCUMENT>\n")
    # xml_foot_maker_end


def dict_maker():
    # title_adding_maker_begin
    with open(new_xml_path, "r") as f:
        title_temp = ",".join(f.readlines())
        par_title = re.compile(r'<key>.+?</key>')
        titles = re.findall(par_title, title_temp)
        with open(new_titles_path, "w") as tf:
            for item in titles:
                tf.write(item.replace("<key>", "").replace("</key>", "") + "\n")
    # title_adding_maker_end


def load_config():
    game_list = []
    with open(path + "/config.txt", "r") as con:
        for line in con.readlines():
            line_list = line.strip().split("\t")
            game_list.append(dict(
                game_name=line_list[0],
                xml_name=line_list[1],
                keys=line_list[2:])
            )
    return game_list

if __name__ == '__main__':
    conf = load_config()
    xml_maker(conf)
    dict_maker()
