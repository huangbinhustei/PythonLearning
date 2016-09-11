# coding=utf-8
import requests
from pyquery import PyQuery as pq
import time
import os
from get_location_and_category import GetList

login_header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
    'Connection': 'keep-alive',
    'Host': 'www.dianping.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
    'Referer': 'http://www.dianping.com/search/category/1/75'
}
s = requests.session()

target = GetList("4", "guangzhou")


def get_shop_detail_from_view_page(shop_url):
    time.sleep(0.2)
    try:
        t_content = pq(s.get(shop_url, headers=login_header).content)(".brief-info")
        return {pq(t_content)(".phone").text(), pq(t_content)(".address").text()}
    except:
        print("唉")
        return {"0", "0"}


def get_shop_detail_from_shop_list(list_url, l):
    r = s.get(list_url, headers=login_header)
    shop_list = pq(r.content)("div").filter("#shop-all-list")

    if not shop_list:
        return
    for shop in pq(shop_list)("ul")("li"):
        temp = pq(shop)(".tit")
        shop_url = pq(temp)("a").attr("href")
        if shop_url in target.shop_has_saved:
            print("has saved\t" + shop_url)
            continue
        print(shop_url)
        shop_name = pq(temp)("a").attr("title")
        info = ["0", "0", "0"]
        if pq(temp)(".promo-icon"):
            d = pq(temp)(".promo-icon")
            if pq(d)(".igroup"):  # 团购
                info[0] = "团购"
            if pq(d)(".ipromote"):  # 促销
                info[1] = "促销"
            if pq(d)(".ibook"):  # 预订
                info[2] = "预订"
        shop_detail = get_shop_detail_from_view_page("http://www.dianping.com" + shop_url)
        with open(target.folder_name + "/shop.txt", "a") as f:
            f.write(
                shop_url + "\t" + shop_name + "\t" +
                "\t".join(info) + "\t" + 
                "\t".join(shop_detail) + "\t" +
                "\t".join(l[1:]) + "\n")
            target.shop_has_saved.add(shop_url)
    if pq(r.content)("div")(".page")("a")(".next").attr("href"):
        return "http://www.dianping.com" + pq(r.content)("div")(".page")("a")(".next").attr("href")


def get_shop(l):
    if not l:
        return
    temp = l[0]
    while 1:
        if not temp:
            break
        temp = get_shop_detail_from_shop_list(temp, l)


if __name__ == '__main__':
    if not os.path.exists(target.folder_name + "/all_list.txt"):
        target.run()

    with open(target.folder_name + "/all_list.txt", "r") as f_all_list:
        for line in f_all_list.readlines():
            get_shop(line.strip().split("\t"))
