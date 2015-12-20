import requests
import re
from pyquery import PyQuery as pq


page_number = 1
last = []
while 1:
    if page_number == 10:
        break
    url = "http://www.qiushibaike.com/8hr/page/" + str(page_number)
    target = requests.get(url).content.decode("utf-8")
    flag_content = pq(target)(".content")
    for item in flag_content:
        a = pq(item).text()
        if len(a) > 20:
            last.append(a.replace(" ", "") + "\n")
    page_number += 1

for item in last:
    try:
        print(item)
    except Exception as e:
        print(e)
