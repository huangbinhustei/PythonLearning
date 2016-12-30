#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import io
from PIL import Image
import os
from collections import defaultdict
from pyquery import PyQuery as pq
import sys

games = defaultdict(lambda: [])
basedir = os.path.abspath(os.path.dirname(__file__))
url_cover = "http://gl.baidu.com/gonglve/api/getcontent"
url_end = "&type=pic&src=cover.jpg"


class ProgressBar:
    def __init__(self, count=0, total=0, width=50):
        self.count = count
        self.total = total
        self.width = width

    def move(self):
        self.count += 1
        sys.stdout.write(' ' * (self.width + 9) + '\r')
        sys.stdout.flush()
        progress = int(self.width * self.count / self.total)
        sys.stdout.write('{0:3}/{1:3}: '.format(self.count, self.total))
        sys.stdout.write('+' * progress + '-' * (self.width - progress) + '\r')
        if progress == self.width:
            sys.stdout.write('\n')
        sys.stdout.flush()


def pic_size_check(t_url):
    try:
        t_temp = requests.get(t_url)
        t_img = Image.open(io.BytesIO(t_temp.content))
        if min(t_img.size) > 120:
            return True
        else:
            return False
    except:
        print(t_url)
        return False


f_out = open(os.path.join(basedir, "mid_output.txt"), "w", encoding="utf-8")
f_error = open(os.path.join(basedir, "mid_error.txt"), "w", encoding="utf-8")


with open(os.path.join(basedir, "input.txt"), "r", encoding="utf-8") as f:
    file_content = [line.strip().split("\t") for line in f.readlines()[1:]]
    bar = ProgressBar(total=len(file_content))

    for item in file_content:
        view_url = item[2]
        doc_id = view_url.split("?")[0].split("/")[-1]
        t_url_cover = url_cover + "?doc_id=" + doc_id + url_end
        if pic_size_check(t_url_cover):
            temp = item
            temp.append(t_url_cover)
            f_out.write("\t".join(temp)+"\n")
            bar.move()
        else:
            view_content = requests.get(view_url).content
            zw = pq(view_content)(".doc-content.doc-content-txt")
            img = pq(zw)("img")
            flag = False
            for ttt in img:
                pic_url = pq(ttt).attr("src")
                if pic_size_check(pic_url):
                    temp = item
                    temp.append(pic_url)
                    f_out.write("\t".join(temp)+"\n")
                    bar.move()
                    flag = True
                    break
            if not flag:
                f_error.write("没有图片\t" + "\t".join(item) + "\n")
                f_out.write("\t".join(item) + "\n")
                bar.move()

f_out.close()
f_error.close()
