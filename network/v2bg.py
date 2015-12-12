from urllib import request
import re
from datetime import datetime
from pyquery import PyQuery as pq


target_url = request.urlopen("http://ng.d.cn/channel/testlist.html").read().decode("utf-8")
start = datetime.now()
pattern1 = r'<td class="name"><a href=.+<h2 class="yjkf">已经开测</h2>'
pattern2 = r'</tr>'
target = re.split(pattern2, re.findall(pattern1, target_url, re.S)[0])

next2result = []
result = []
final = []
for item in target:
    small_item = re.findall(r'<td.+</td>', item)
    for item_kuaile in small_item:
        next2result.append(item_kuaile)
for i in range(len(next2result)):
    if i % 6 == 0 or i % 6 ==3:
        result.append(next2result[i])

a = "".join(result)

v_source = pq(a)
b = v_source("td")
for i in pq(a):
    final.append(pq(i).text().split(" "))

print(final)
for_print = []

# for i in range(len(final)):
#     if not for_print[i//4]:
#         for_print.append("")
#     for_print[i//4] = "".join(final[i])
#
# print(for_print)
