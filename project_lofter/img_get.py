# -*- coding: utf-8 -*-
import requests
from pyquery import PyQuery as pq
import os
import re
from picsave import PicSave
import time
import logging
logging.basicConfig(level=logging.INFO)

img_src_has_try2save = set([])

target_list = [
    (
        "wowosyyhu",
        ([".main", ".img"], "a", ".img"),
        re.compile(r'http://wowosyyhu\.lofter\.com/post/(.+)')
    ), (
        "wowowak",
        ([".main", ".img"], "a", ".img"),
        re.compile(r'http://wowowak\.lofter\.com/post/(.+)')
    ), (
        "idheihei",
        ([".main", ".img"], "a", ".img"),
        re.compile(r'http://idheihei\.lofter\.com/post/(.+)')
    )
]

# http://12ofme.lofter.com/
target_item = target_list[1]

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
    'Connection': 'keep-alive',
    'Host': "http://" + target_item[0] + ".lofter.com/",
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
    # 'Referer': 'http://www.163.com/special/00774IMC/lofter_v13.html',
}


def get_img_src(tar_url):
    # 根据post的地址，提取img的地址
    temp_set_of_img_src = set([])
    r = requests.get(tar_url)
    if r.status_code != 200:
        logging.error("打不开：" + tar_url + str(r.status_code))
        return set([])
    target_content = r.content
    target_div = pq(target_content)("div")
    target_img = pq(target_div)(x_path_post[2])
    target_a = pq(target_img)("a")
    for item in target_a:
        img_src_item = pq(item).attr("bigimgsrc")
        if img_src_item not in img_src_has_try2save:
            temp_set_of_img_src.add(img_src_item)
            img_src_has_try2save.add(img_src_item)
    return temp_set_of_img_src


def get_post_url(target_url):
    set_of_post_url = set([])
    # 根据列表页的地址，提取post地址
    r = requests.get(target_url)
    if r.status_code != 200:
        logging.error("打不开：" + target_url + str(r.status_code))
        return set([])
    target = r.content
    flags_title = pq(target)(x_path_post[0][0])(x_path_post[0][1])
    for item in pq(flags_title)(x_path_post[1]):
        set_of_post_url.add(pq(item).attr("href"))
    return set_of_post_url


class Student(object):
    def __init__(self, url_begin):
        self.set_of_img_src = set([])
        self.ind = 0
        self.url = url_begin
        self.pattern = pat
        self.temp = set([])  # 用来判断是否抓取完毕的，感觉略诡异
        self.flag = True

    def start(self):
        # 构造列表页（翻页）的地址，并分别提取每一页
        page_number = 33
        while self.flag:
            page_url = self.url + "?page=" + str(page_number)
            if page_number == 1:
                page_url = self.url
            page_number += 1
            logging.info(page_url)
            self.func_in_try(page_url)  # 一页一页的抓取
            time.sleep(1)

    def func_in_try(self, this_url):
        for post_url in get_post_url(this_url):
            post_name = str(re.sub(self.pattern, r'\1', post_url))
            if post_name in post_has_try2save:
                # 整理过了，需要查漏补缺，现在先跳过
                logging.info(post_name)
                # self.flag = False
                continue
            post_has_try2save.add(post_name)
            img_set = get_img_src(post_url)  # img_list = 这一页的图片url list
            new_save_p.update(img_set, post_name)
            new_save_p.start_save()
            self.flag = True
        return True


if __name__ == '__main__':
    url = "http://" + target_item[0] + ".lofter.com/"
    x_path_post = target_item[1]
    path = os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/" + target_item[0] + "/"
    if not os.path.exists(path):
        os.makedirs(path)
        logging.info("os.makedirs:" + target_item[0])
    if os.path.exists(path + "log.txt"):
        with open(path + "log.txt", "r") as f:
            post_has_try2save = set([item.split("\t")[0] for item in f.readlines()])
    else:
        post_has_try2save = set([])
    pat = target_item[2]
    new_lol = Student(url)
    new_save_p = PicSave({}, " ", path)
    new_lol.start()
