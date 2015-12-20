import requests
import re
from pyquery import PyQuery as pq


page_number = 1
url = "http://www.qiushibaike.com/8hr/page/" + str(page_number)
target = requests.get(url).content.decode("utf-8")
target = target.replace(u"\xa0", u"")
flags = pq(target)("div")
flags = pq(flags).children()
for item in flags:
    x = pq(item).text()
    print(type(x))
    x = x.encode("cp936")
    print(x.decode("cp936"))
    # print(pq(item).text())








# flags = re.findall(r'<div class="content">(.+?)</div>', target, re.S)
# for item in flags:
#     print(item)


