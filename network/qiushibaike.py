import requests
import re
from pyquery import PyQuery as pq


page_number = 1
txt_output = []
pic_output = []
while page_number < 2:
    try:
        url = "http://www.qiushibaike.com/8hr/page/" + str(page_number)
        target = requests.get(url).content.decode("utf-8")
        flag_content = pq(target)(".content")
        for item in flag_content:
            a = pq(item).text()
            if pq(item).next().has_class("thumb"):
                find_pic = pq(pq(pq(item).next())("img")).attr("src")
                pic_output.append([a, find_pic])
                continue
            txt_output.append(a.replace(" ", "") + "\n")
        page_number += 1
    except Exception as e:
        print(e)

for item in txt_output:
    pass
    print(item)


print("\n" + "*"*100 + "\n")


for item in pic_output:
    print(item[0] + "\n" + item[1])
