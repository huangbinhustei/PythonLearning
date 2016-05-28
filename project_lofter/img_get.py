# -*- coding: utf-8 -*-
import requests
from pyquery import PyQuery as pq
import os
import re
from picsave import PicSave
import time


img_src_has_try2save = set([])
post_has_try2save = {" ", " "}

target_list = [
     (
        "wowosyyhu",
        ([".main", ".img"], "a", ".img"),
        re.compile(r'http://wowosyyhu\.lofter\.com/post/(.+)')
    ), (
        "nlrzjghxxx",
        ([".main", ".img"], "a", ".img"),
        re.compile(r'http://nlrzjghxxx\.lofter\.com/post/(.+)'),
    ), (
        "onlyecholy",
        ([".pic", ".img"], "a", ".pic"),
        re.compile(r'http://onlyecholy\.lofter\.com/post/(.+)')
    ), (
        "9110911",
        ([".main", ".img"], "a", ".img"),
        re.compile(r'http://9110911\.lofter\.com/post/(.+)')
    ), (
        "wzwdkcm",
        ([".pic", ".img"], "a", ".pic"),
        re.compile(r'http://wzwdkcm\.lofter\.com/post/(.+)')
    ), (
        "dylank",
        ([".pic", ".img"], "a", ".pic"),
        re.compile(r'http://dylank\.lofter\.com/post/(.+)')
    ), (
        "wowowak",
        ([".main", ".img"], "a", ".img"),
        re.compile(r'http://wowowak\.lofter\.com/post/(.+)')
    ), (
        "380830138",
        ([".main", ".img"], "a", ".img"),
        re.compile(r'http://380830138\.lofter\.com/post/(.+)')
    ), (
        "idheihei",
        ([".main", ".img"], "a", ".img"),
        re.compile(r'http://380830138\.lofter\.com/post/(.+)')
    )
]

# http://12ofme.lofter.com/
# http://fuliti.lofter.com/
target_item = target_list[4]
# s = requests.session()

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
    'Connection': 'keep-alive',
    'Host': "http://" + target_item[0] + ".lofter.com/",
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
    # 'Referer': 'http://www.163.com/special/00774IMC/lofter_v13.html',
}


class Student(object):
    def __init__(self, url_begin):
        self.set_of_post_url = set([])
        self.set_of_img_src = set([])
        self.ind = 0
        self.url = url_begin
        self.pattern = pat
        self.temp = set([])  # 用来判断是否抓取完毕的，感觉略诡异

    def get_post_url(self, target_url):
        # 根据列表页的地址，提取post地址
        target = requests.get(target_url).content.decode("utf-8")

        flags_title = pq(pq(target)(x_path_post[0][0]))(x_path_post[0][1])
        for item in pq(flags_title)(x_path_post[1]):
            self.set_of_post_url.add(pq(item).attr("href"))

        return self.set_of_post_url

    def get_img_src(self, tar_url):
        # 根据post的地址，提取img的地址
        temp_set_of_img_src = set([])
        target_content = requests.get(tar_url).content.decode("utf-8")
        target_div = pq(target_content)("div")
        target_img = pq(target_div)(x_path_post[2])
        target_a = pq(target_img)("a")
        for item in target_a:
            img_src_item = pq(item).attr("bigimgsrc")
            if img_src_item not in img_src_has_try2save:
                temp_set_of_img_src.add(img_src_item)
                img_src_has_try2save.add(img_src_item)
        return temp_set_of_img_src

    def start(self):
        # 构造列表页（翻页）的地址，并分别提取每一页
        page_number = 1
        while 1:
            temp_url = self.url + "?page=" + str(page_number)
            if page_number == 1:
                temp_url = self.url
            page_number += 1
            print(temp_url)
            self.func_in_try(temp_url)  # 一页一页的抓取
            time.sleep(2)

    def func_in_try(self, this_url):
        post_url_set = self.get_post_url(this_url)
        for post_url in post_url_set:
            dir_name = str(re.sub(self.pattern, r'\1', post_url))
            if dir_name in post_has_try2save:
                # print("[本次已整理]\t\t" + post_url)
                continue
            post_has_try2save.add(dir_name)
            # try:
            img_set = self.get_img_src(post_url)  # img_list = 这一页的图片url list
            dir_path = path + dir_name + "/"
            if not os.path.exists(dir_path):
                print("[  全新整理]\t\t" + post_url)
                # 文件夹不存在就创建并尝试抓取
                os.makedirs(dir_path)
                new_save_p.update(img_set, dir_path)
                new_save_p.start_save()
            else:
                # 如果文件夹存在就可能需要判重了
                log_path = dir_path + "save_log.txt"
                if not os.path.exists(log_path):
                    new_save_p.update(img_set, dir_path)
                    new_save_p.start_save()
                    print("[需全部重整]\t\t " + post_url)
                else:
                    img_set_need_retry = set([])
                    with open(log_path, "r") as f:
                        for line in f.readlines():
                            log_line = line.split("\t")
                            if log_line[0] == "failed":
                                img_set_need_retry.add(log_line[1])
                    if img_set_need_retry:
                        print("[  文件补漏]\t\t " + post_url)
                        new_save_p.update(img_set_need_retry, dir_path)
                        new_save_p.start_save()
                    else:
                        print("[上次已整理]\t\t " + post_url)
        return True


if __name__ == '__main__':
    url = "http://" + target_item[0] + ".lofter.com/"
    x_path_post = target_item[1]
    path = os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/" + target_item[0] + "/"
    pat = target_item[2]

    new_lol = Student(url)
    new_save_p = PicSave({}, " ")
    new_lol.start()
