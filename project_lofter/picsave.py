# -*- coding: utf-8 -*-
import requests
import os
import hashlib
import threading
from PIL import Image

min_pic_size = 300000


def get_md5(need2md5):
    md5 = hashlib.md5()
    md5.update(need2md5.encode("utf-8"))
    return md5.hexdigest()


class PicSave(object):
    def __init__(self, url_set, post_name, basedir, retry_time=3):
        self.pic_url_set = url_set
        self.save_log = []
        self.post_name = post_name
        self.retry_time = retry_time
        self.basedir = basedir

    def update(self, url_set_new, post_new=" ", basedir_new=" "):
        self.pic_url_set = url_set_new
        self.save_log = []
        if post_new != " ":
            self.post_name = post_new
        if basedir_new != " ":
            self.basedir = basedir_new

    def save_one_picture(self, item_url):
        flag = "failed"
        pic_name = str(get_md5(item_url)) + ".jpg"
        pic_path = self.basedir + self.post_name + "_" + pic_name
        for i in range(self.retry_time):
            try:
                pic_target = requests.get(item_url, timeout=20)
            except Exception as e:
                continue
            if 404 == pic_target.status_code:
                flag = "404"
                continue
            c_length = pic_target.headers["Content-Length"]
            if not c_length or int(c_length) < min_pic_size:
                flag = "small:" + str(c_length)
                continue
            with open(pic_path, "wb") as f:
                f.write(pic_target.content)
            saved_size = os.path.getsize(pic_path)
            if int(c_length) == int(saved_size):
                flag = "done = " + str(i+1) + " " + str(c_length)
                break
        self.save_log.append([self.post_name, item_url, pic_name, flag])
        return [self.post_name, item_url, pic_name, flag]

    def log_writing(self, kind):
        with open(self.basedir + "log.txt", kind) as s_log:
            for list_item in self.save_log:
                s_log.write("\t".join(list_item) + "\n")

    def start_save(self):
        if not self.pic_url_set:
            print("没有 url list")
            return
        th = []
        for item_url in self.pic_url_set:
            th.append(threading.Thread(target=self.save_one_picture, args=(item_url,)))
        for t in th:
            t.setDaemon(True)
            t.start()
        for t in th:
            t.join()
        self.log_writing("a")

    def re_save_by_log(self):
        print("\nre_save_by_log\n")
        re_write_flag = False
        with open(self.basedir + "log.txt", "r") as f:
            lines = [line.strip().split("\t") for line in f.readlines()]

        self.save_log = []
        for line in lines:
            if "done" in line[3] or "small" in line[3] or "404" in line[3]:
                self.save_log.append(line)
            else:
                re_write_flag = True
                self.post_name = line[0]
                self.save_one_picture(line[1])
        if re_write_flag:
            self.log_writing("w")
