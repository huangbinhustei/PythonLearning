# -*- coding: utf-8 -*-

import os
import requests

min_pic_size = 500000
path = os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/idheihei/"


def save_one_picture(line):
    flag = "failed"
    post_name, item_url, pic_name = line
    pic_path = path + post_name + "_" + pic_name
    for i in range(3):
        try:
            pic_target = requests.get(item_url, timeout=20)
        except Exception as e:
            continue
        c_length = pic_target.headers["Content-Length"]
        if not c_length or int(c_length) < min_pic_size:
            flag = "small:" + str(c_length)
            continue
        with open(pic_path, "wb") as f:
            f.write(pic_target.content)
        saved_size = os.path.getsize(pic_path)
        if int(c_length) == int(saved_size):
            flag = "done = " + str(i + 1) + " " + str(c_length)
            print(pic_name)
            break
    return [post_name, item_url, pic_name, flag]

with open("/Users/baidu/Documents/百度/Git/PythonLearning/project_lofter/idheihei/log.txt", "r") as f:
    lines = [line.strip().split("\t") for line in f.readlines()]

with open("/Users/baidu/Documents/百度/Git/PythonLearning/project_lofter/idheihei/log.txt", "w") as f:
    for line in lines:
        if "done" in line[3] or "small" in line[3]:
            f.write("\t".join(line) + "\n")
            continue
        n = save_one_picture(line)
        f.write("\t".join(n) + "\n")