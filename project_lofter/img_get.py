# -*- coding: utf-8 -*-
import requests
from pyquery import PyQuery as pq
import os
import re
from picsave import PicSave
import time

path = os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/IMG/"
img_src_has_try2save = set([])
post_has_try2save = {" ", " "}
url = "http://justinbieber520.lofter.com/"


class Student(object):
    def __init__(self, url_begin):
        self.set_of_post_url = set([])
        self.set_of_img_src = set([])
        self.ind = 0
        self.url = url_begin
        self.pattern = re.compile(r'http://justinbieber520\.lofter\.com/post/(.+)')

    def get_sub_url(self, target_url):
        # 根据列表页的地址，提取post地址
        target = requests.get(target_url).content.decode("utf-8")
        flags_title = pq(target)(".pic")
        flags_title = pq(flags_title)(".img")
        for item in pq(pq(flags_title)("a")):
            self.set_of_post_url.add(pq(item).attr("href"))
        return self.set_of_post_url

    def get_img_src(self, tar_url):
        # 根据post的地址，提取img的地址
        temp_set_of_img_src = set([])
        target_content = requests.get(tar_url).content.decode("utf-8")
        target_div = pq(target_content)("div")
        target_img = pq(target_div)(".pic")
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
        post_url_set = self.get_sub_url(this_url)
        if not any(post_url_set):
            print("抓取完毕")
            exit()
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
                        # print("find sth need retry")
                        new_save_p.update(img_set_need_retry, dir_path)
                        new_save_p.start_save()
                    else:
                        print("[上次已整理]\t\t " + post_url)
        return True

if __name__ == '__main__':
    new_lol = Student(url)
    new_save_p = PicSave({}, " ")
    new_lol.start()
