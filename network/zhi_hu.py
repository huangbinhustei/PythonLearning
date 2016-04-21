import requests
from pyquery import PyQuery as pq
import time
import os
import threading
import re
from random import uniform
import sqlite3

login_header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
    'Connection': 'keep-alive',
    'Host': 'www.zhihu.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
    'Referer': 'https://www.zhihu.com/',
}


def login():
    url_1 = "https://www.zhihu.com"
    url = "https://www.zhihu.com/login/email"
    data = {
        "_xsrf": " ",
        "password": "linshi123456",
        "email": "huangbinhustei@gmail.com",
        "captcha": " "
    }

    s = requests.session()

    def get_xsrf(this_url=None):
        r = s.get(this_url, headers=login_header)
        this_xref = re.search(r'(?<=name="_xsrf" value=")[^"]*(?="/>)', r.text)
        if this_xref is None:
            return ''
        else:
            return this_xref.group(0)

    xsrf = get_xsrf(url_1)
    captcha_url = "http://www.zhihu.com/captcha.gif"
    captcha = s.get(captcha_url, stream=True)

    with open("captcha.gif", "wb") as f:
        for line in captcha.iter_content(10):
            f.write(line)

    captcha_str = input("输入验证码\n")
    data["_xsrf"] = xsrf.encode("utf-8")
    data["captcha"] = captcha_str

    res = s.post(url, headers=login_header, data=data)
    print(res.status_code)
    print(res.cookies)
    m_cookies = res.cookies

    test_url = "https://www.zhihu.com"
    res = s.get(test_url, headers=login_header, cookies=m_cookies)
    # print(pq(res).text())
    print(pq(res.con).html())
    # print(pq(res).text())
    # target = pq(res)("h2")
    # for item in target:
    #     print(pq(item).text())

if __name__ == "__main__":
    login()
