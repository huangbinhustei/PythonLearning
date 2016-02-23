# -*- coding: utf-8 -*-
import requests
import os
from pyquery import PyQuery as pq
import hashlib
import threading


def get_md5(need2md5):
    md5 = hashlib.md5()
    md5.update(need2md5.encode("utf-8"))
    return md5.hexdigest()


class PicSave(object):

    def __init__(self, url_set, dir_path, retry_time=3):
        self.set_of_img_src = set([])
        self.pic_url_set = url_set
        self.save_log = []
        self.path = dir_path
        self.retry_time = retry_time

    def update(self, url_set_new, path_new=" "):
        self.pic_url_set = url_set_new
        self.save_log = []
        if path_new == " ":
            return
        self.path = path_new

    def save_once(self, item_url):
        if item_url in self.set_of_img_src:
            flag = "has_saved"
            self.save_log.append([flag, item_url, " "])
            return

        flag = "failed"
        pic_name = str(get_md5(item_url)) + ".jpg"
        pic_path = self.path + pic_name
        for i in range(self.retry_time):
            try:
                pic_target = requests.get(item_url, timeout=10)
            except Exception as e:
                continue
            c_length = pic_target.headers["Content-Length"]
            if not c_length or int(c_length) < 3000:
                print("c_length 不存在或小于3000")
                print("Content-Length:\t\t" + str(c_length))
                continue
            with open(pic_path, "wb") as f:
                f.write(pic_target.content)
            saved_size = os.path.getsize(pic_path)
            if int(c_length) == int(saved_size):
                flag = "succeed = " + str(i+1) + " " + str(c_length)
                self.set_of_img_src.add(item_url)
                break
        self.save_log.append([flag, item_url, pic_name])

    def start_save(self):
        if not self.pic_url_set:
            print("没有 url list")
            return
        th = []
        for item_url in self.pic_url_set:
            th.append(threading.Thread(target=self.save_once, args=(item_url,)))
        for t in th:
            t.setDaemon(True)
            t.start()
        for t in th:
            t.join()
        with open(self.path + "save_log.txt", "a") as s_log:
            for list_item in self.save_log:
                s_log.write(list_item[0] + "\t" + list_item[1] + "\t" + list_item[2] + "\n")


if __name__ == '__main__':

    def construct_pic_list():
        url = "http://wow.178.com/201602/249293362615.html"
        target = requests.get(url).content

        textbox = pq(pq(target)("div"))(".textBox")
        cont = pq(textbox)("img")
        pic_set = set([])

        for it1em in cont:
            pic_set.add(pq(it1em).attr("src"))
        return pic_set

    path = os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/"
    temp_set = construct_pic_list()

    test_save = PicSave(temp_set, path)
    test_save.start_save()
