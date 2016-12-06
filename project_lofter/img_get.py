# -*- coding: utf-8 -*-
import requests
from pyquery import PyQuery as pq
import os
import re
from picsave import PicSave
import time
import logging
import threading
from functools import reduce
logging.basicConfig(level=logging.INFO)

img_src_has_try2save = set([])

target_list = [
    (
        "sys-peter",
        ([".pic", ".img"], "a", ".img"),
        re.compile(r'http://sys-peter\.lofter\.com/post/(.+)')
    ), (
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
target_item = target_list[2]
# http://12ofme.lofter.com/
# http://fuliti.lofter.com/
# http://vivian0610.lofter.com/?page=7&t=1475136637039


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
    'Connection': 'keep-alive',
    'Host': "http://" + target_item[0] + ".lofter.com/",
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
    # 'Referer': 'http://www.163.com/special/00774IMC/lofter_v13.html',
}


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
    page_offset = 30

    def __init__(self, url_begin):
        self.set_of_img_src = set([])
        self.url = url_begin
        self.flag = []
        self.big_flag = True
        self.save_log = []

    def get_img_src_and_save(self, tar_url):
        post_name = str(re.sub(pat, r'\1', tar_url))
        if post_name in post_has_try2save:
            # 整理过了，需要查漏补缺，现在先跳过
            logging.info("done" + post_name)
            self.flag.append(False)
            return
        post_has_try2save.add(post_name)
        self.flag.append(True)

        # 根据post的地址，提取img的地址
        temp_set_of_img_src = set([])
        r = requests.get(tar_url)
        if r.status_code != 200:
            logging.error("打不开：" + tar_url + str(r.status_code))
            return

        for item in pq(r.content)("div")(x_path_post[2])("a"):
            img_src_item = pq(item).attr("bigimgsrc")
            if img_src_item not in img_src_has_try2save:
                temp_set_of_img_src.add(img_src_item)
                img_src_has_try2save.add(img_src_item)
        new_save_p = PicSave(temp_set_of_img_src, post_name, path)
        new_save_p.start_save()

    def finish_check(self):
        if self.flag:
            self.big_flag = reduce(lambda x, y: x and y, self.flag)
        else:
            self.big_flag = False

    def start(self):
        # 构造列表页（翻页）的地址，并分别提取每一页
        page_offset = 0
        while self.big_flag:
            page_offset += 1
            page_url = self.url + "?page=" + str(page_offset)
            if 1 == page_offset:
                page_url = self.url
            logging.info(page_url)
            self.flag = []

            post_url_set = get_post_url(page_url)

            th = []
            for post_url in post_url_set:
                th.append(threading.Thread(target=self.get_img_src_and_save, args=(post_url,)))
            for t in th:
                t.setDaemon(True)
                t.start()
            for t in th:
                t.join()

            self.finish_check()
            time.sleep(0.5)

        re_save_p = PicSave(set([]), " ", path)
        re_save_p.re_save_by_log()


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
    new_lol.start()
