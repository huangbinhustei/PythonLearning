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


def log_rewrite(log_file_name):
    data = []
    set_url_this_page = []  # 这一页的所有图片url
    flag_tuple = ("succeed", "has_saved", "failed")

    def row_filter(rows, this_str):
        for temp in rows:
            if not temp[0].find(this_str) == 0:
                continue
            if temp[1] in set_url_this_page:
                continue
            set_url_this_page.append(temp[1])
            data.append(temp)

    if not os.path.exists(log_file_name):
        return
    with open(log_file_name, "r") as old_log:
        t_row = []
        for lines in old_log.readlines():
            temp_row = lines.split("\t")
            t_row.append(temp_row)
        for flag in flag_tuple:
            row_filter(t_row, flag)

    with open(log_file_name, "w") as f:
        for lines in data:
            f.write("\t".join(lines))


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

    def save_one_picture(self, item_url):
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
                print("Content-Length不存在或过小:\t" + str(c_length))
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
            th.append(threading.Thread(target=self.save_one_picture, args=(item_url,)))
        for t in th:
            t.setDaemon(True)
            t.start()
        for t in th:
            t.join()
        with open(self.path + "save_log.txt", "a") as s_log:
            for list_item in self.save_log:
                s_log.write(list_item[0] + "\t" + list_item[1] + "\t" + list_item[2] + "\n")
        log_rewrite(self.path + "save_log.txt")


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
