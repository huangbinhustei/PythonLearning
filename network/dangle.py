import requests
import re
from datetime import datetime
from pyquery import PyQuery as pq

target_url = requests.get("http://ng.d.cn/channel/testlist.html").content

res = pq(target_url)("tr")
spaces = re.compile(r' {2,11}')

today = datetime.now()
i = True
for item in res:
    remove_space_1 = pq(item).text().replace(u"\xa0\r\n\t", u"")
    remove_space_2 = re.sub(spaces, "|", remove_space_1)
    temp_list = remove_space_2.strip().split(" ")
    if i:
        i = False
        continue
    try:
        date = temp_list[2].split("-")
        last_second = datetime(2015, int(date[0]), int(date[1]), 23, 59)
        if last_second > today:
            print(temp_list[:3])
    except:
        pass
