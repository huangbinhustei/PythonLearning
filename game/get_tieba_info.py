# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
import requests
import logging
logging.basicConfig(level=logging.INFO)

game_types = [
    ['客户端网游',    '/f/index/forumpark?cn=%BF%CD%BB%A7%B6%CB%CD%F8%D3%CE&ci=0&pcn=%D3%CE%CF%B7&pci=0&ct=1&rn=20&pn=1'],
    # ['桌游',        '/f/index/forumpark?cn=%D7%C0%D3%CE&                  ci=0&pcn=%D3%CE%CF%B7&pci=0&ct=1&rn=20&pn=1'],
    # ['游戏角色',    '/f/index/forumpark?cn=%D3%CE%CF%B7%BD%C7%C9%AB&      ci=0&pcn=%D3%CE%CF%B7&pci=0&ct=1&rn=20&pn=1'],
    # ['网页版网游',  '/f/index/forumpark?cn=%CD%F8%D2%B3%B0%E6%CD%F8%D3%CE&ci=0&pcn=%D3%CE%CF%B7&pci=0&ct=1&rn=20&pn=1'],
    # ['手机游戏', '/f/index/forumpark?cn=%CA%D6%BB%FA%D3%CE%CF%B7&         ci=0&pcn=%D3%CE%CF%B7&pci=0&ct=1&rn=20&pn=1'],
    # ['小游戏', '/f/index/forumpark?cn=%D0%A1%D3%CE%CF%B7&                 ci=0&pcn=%D3%CE%CF%B7&pci=0&ct=1&rn=20&pn=1'],
    # ['单机游戏', '/f/index/forumpark?cn=%B5%A5%BB%FA%D3%CE%CF%B7&         ci=0&pcn=%D3%CE%CF%B7&pci=0&ct=1&rn=20&pn=1'],
    # ['掌机游戏', '/f/index/forumpark?cn=%D5%C6%BB%FA%D3%CE%CF%B7&         ci=0&pcn=%D3%CE%CF%B7&pci=0&ct=1&rn=20&pn=1'],
    # ['电视游戏', '/f/index/forumpark?cn=%B5%E7%CA%D3%D3%CE%CF%B7&         ci=0&pcn=%D3%CE%CF%B7&pci=0&ct=1&rn=20&pn=1'],
    # ['其他游戏及话题', '/f/index/forumpark?cn=%C6%E4%CB%FB%D3%CE%CF%B7%BC%B0%BB%B0%CC%E2&ci=0&pcn=%D3%CE%CF%B7&pci=0&ct=1&rn=20&pn=1'],
]
s = requests.session()


def init_s():
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'tieba.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36',
    }
    s.headers.update(header)
    s.verify = False

init_s()
url = "http://tieba.baidu.com/f/index/forumpark"

data = dict(
    cn="客户端网游",
    ci=0,
    pcn="游戏",
    pci=0,
    ct=1,
    rn=20,
    pn=1
)

r = s.get(url, params=data)
print(r.url)

ba = pq(r.content)(".ba_content")
print(ba)

ba_1 = ba[0]

print(pq(pq(ba_1)("p")[0]).text())
print(pq(pq(pq(ba_1)("p")[1])(".ba_p_num")).text())
print(pq(pq(pq(ba_1)("p")[1])(".ba_m_num")).text())