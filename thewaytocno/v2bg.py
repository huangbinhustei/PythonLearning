from urllib import request
import re
from datetime import datetime

start = datetime.now()


target_url = request.urlopen("file:///C:/Users/%E5%BD%AC%E6%AD%86/Desktop/%E5%BD%93%E4%BA%86.html").read().decode("utf-8")
pattern1 = r'<td class="name"><a href=.+<h2 class="yjkf">已经开测</h2>'
pattern2 = r'</tr>'
target = re.split(pattern2, re.findall(pattern, target_url, re.S)[0])

next2result = []
result = []
for item in target:
    small_item = re.findall(r'<td.+</td>', item)
    for item_kuaile in small_item:
        next2result.append(item_kuaile)
for i in range(len(next2result)):
    if i % 6 < 3:
        result.append(next2result[i])

for i in result:
    print(i)

