# coding=utf-8
import requests
from pyquery import PyQuery as pq
import time
import os

login_header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
            'Connection': 'keep-alive',
            'Host': 'www.dianping.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
            'Referer': 'https://www.dianping.com/',
        }
s = requests.session()
url_root_www = "http://www.dianping.com/"
url_root = "http://www.dianping.com/search/category/"
path_root = "/Users/baidu/Documents/百度/Git/PythonLearning/job/"


class GetList(object):
    def __init__(self, zone_code, zone_name):
        self.code = zone_code
        self.name = zone_name
        self.par_url_header = "/search/category/" + self.code + "/75/"
        self.folder_name = path_root + self.name
        self.url_for_level_one = url_root + self.code + "/75"

        self.shop_has_saved = set([])
        t_path_shop = self.folder_name + "/shop.txt"
        if os.path.exists(t_path_shop):
            with open(t_path_shop, "r") as f_shop:
                for line in f_shop.readlines():
                    self.shop_has_saved.add(line.strip().split("\t")[0])

    def update(self, zone_code, zone_name):
        self.code = zone_code
        self.name = zone_name
        self.par_url_header = "/search/category/" + self.code + "/75/"
        self.folder_name = path_root + self.name
        self.url_for_level_one = url_root + self.code + "/75"

    def get_level_one(self):
        url = self.url_for_level_one
        root = s.get(url, headers=login_header).content
        location_level_one = []
        loc = pq(root)("div").filter("#bussi-nav")
        for item in pq(loc)("a"):
            location_level_one.append([pq(item).attr("href"), pq(item).text()])
            # print(pq(item).attr("href") + "\t" + pq(item).text())
        category_level_one = []
        cat = pq(root)("div").filter("#classfy")
        for item in pq(cat)("a"):
            category_level_one.append([pq(item).attr("href"), pq(item).text()])
            # print(pq(item).attr("href") + "\t" + pq(item).text())
        final = [location_level_one, category_level_one]
        return final

    def get_level_two(self, level1, kind="location"):
        if kind == "location":
            txt_path = self.folder_name + "/path_loc.txt"
            x_path = "#bussi-nav-sub"
            target = level1[0]
        else:
            txt_path = self.folder_name + "/path_category.txt"
            x_path = "#classfy-sub"
            target = level1[1]
        with open(txt_path, "w") as f:
            for item in target:
                print(item[0])
                time.sleep(0.5)
                l1 = s.get("http://www.dianping.com" + item[0], headers=login_header).content
                l2 = pq(l1)("div").filter(x_path)
                for s_item in pq(l2)("a")[1:]:
                    f.write(
                        pq(s_item).attr("href").replace(self.par_url_header, "") +
                        "\t" + item[1] + "\t" + pq(s_item).text() + "\n"
                    )

    def make_list(self):
        url_head = self.url_for_level_one
        login_header["Referer"] = url_head
        g_item = []
        r_item = []
        with open(self.folder_name + "/path_category.txt", "r") as f1:
            for g_line in f1.readlines():
                g_item.append(g_line.strip().split("\t"))
        with open(self.folder_name + "/path_loc.txt", "r") as f2:
            for r_line in f2.readlines():
                r_item.append(r_line.strip().split("\t"))
        with open(self.folder_name + "/all_list.txt", "w") as f:
            for x in g_item:
                for y in r_item:
                    f.write(
                        url_head + "/" + x[0] + y[0]
                        + "\t" + x[1] + "\t" + x[2]
                        + "\t" + y[1] + "\t" + y[2] + "\n"
                    )

    def run(self):
        if not os.path.exists(self.folder_name):
            os.mkdir(self.folder_name)

        level1 = self.get_level_one()
        self.get_level_two(level1, "location")
        self.get_level_two(level1, "category")

        self.make_list()
