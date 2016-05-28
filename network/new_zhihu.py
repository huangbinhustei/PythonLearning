# -*- coding: utf-8 -*-

import requests
from pyquery import PyQuery as pq

login_header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Connection': 'keep-alive',
    'Host': 'www.zhihu.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36 Core/1.47.277.400 QQBrowser/9.4.7658.400',
    'Cookie': 'udid="AJAAMUDDlQmPToKPZs1CQA7XgrfmlJlKLFM=|1457618913"; _zap=72136e16-c52f-45dd-8f7f-30f221c0e229; d_c0="AFDAhXpGogmPTuvLBtB1t4jMtZAhX47MZjE=|1460885794"; q_c1=6083c3c72f6b4757ba6bb000267ddf9b|1462010933000|1462010933000; l_cap_id="NzJhMDQzYzRlNDhhNDY5ODhkYTk1YzBjNmQyODViNTM=|1462172814|cfa2cedf4ff3b66d6cb9d9607596eba363a2fbc7"; cap_id="ZmJmZWQ3OTQ1ZDE2NGMzYWI0M2M2N2E3NWNmODI3NmU=|1462172814|148ee5e163024e879a44a73211516dfa51aed0de"; login="YmU3OTg1ZTU3YzAwNDE0ZjgwYmZmNTljNWM2YjI0ZDc=|1462172828|f112e4faa43deb780b61524751d97672864fc825"; z_c0=Mi4wQUFBQXRta1pBQUFBVU1DRmVrYWlDUmNBQUFCaEFsVk5wWWxPVndDMnF3dEhJSzdoYUp6Q3k5Mm9ZbnAtb3Nhendn|1462172837|24afa31dee37b2dbcaf46d0742970abf038bd542; __utmt=1; __utma=51854390.168328783.1462458208.1462799694.1462886591.11; __utmb=51854390.4.10.1462886591; __utmc=51854390; __utmz=51854390.1462799694.10.3.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmv=51854390.100-1|2=registration_date=20120614=1^3=entry_date=20120614=1'
}

feed_data = {
    "params": r'''{"offset":10,"start":"10"}''',
    "method": "next"
}

target = requests.get("https://www.zhihu.com/", headers=login_header).content

h2s = pq(target)("h2")

for item in h2s:
    print(pq(item).text())

target_2 = requests.get("https://www.zhihu.com/node/HomeFeedListV2", headers=login_header).content
h2s_2 = pq(target_2)("h2")
for item in h2s_2:
    try:
        print(pq(item).text())
    except:
        print("hha")
        pass
    try:
        print(pq(pq(item)("a")).text())
    except:
        print("11111111hha")
        pass

