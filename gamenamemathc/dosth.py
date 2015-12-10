import os
from datetime import datetime

game_name = []
result = []
wen_dang = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/doclist_mini.txt"
namelist = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/userdict/gamename.txt"
result_file = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/result.txt"

start = datetime.now()

with open(namelist, "r", encoding="utf-8") as txt111:
    for item in txt111.readlines():
        game_name.append(item.strip())


print(datetime.now()-start)
with open(wen_dang, "r", encoding="utf-8") as data:
    for item in data.readlines():
        count = 0
        temp = []
        for name in game_name:
            if item.find(name) > -1:
                temp.append(name)
                count += 1
        result.append([item, temp])

print(datetime.now()-start)
with open(result_file, "w", encoding="gbk") as f:
    for item in result:
        last_for_write = str(item[0].strip()) + "\t" + str(item[1]) + "\n"
        f.write(last_for_write)
