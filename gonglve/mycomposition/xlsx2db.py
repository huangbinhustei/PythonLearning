import xlrd
import time
from data import Docs, db

genre_map = {
"议论文":0,
"记叙文":1,
"说明文":2,
"读后感":3,
"散文":4,
"日记":5,
"其他":6,
}


print("start")
zuowen1 = xlrd.open_workbook("/Users/baidu/Desktop/1/zuowen_2.xlsx").sheet_by_index(0)
print("load")
for i in range(zuowen1.nrows):
	if i == 0:
		continue
	doc_md = zuowen1.cell_value(i,8).replace("http://gl.baidu.com/view/","")
	title = zuowen1.cell_value(i,1)
	content = zuowen1.cell_value(i,9)
	grade = zuowen1.cell_value(i,4)
	genre = genre_map[zuowen1.cell_value(i,5)]
	words = int(zuowen1.cell_value(i,2))
	view = zuowen1.cell_value(i,7)
	former_url = zuowen1.cell_value(i,8)
	create_time = int(time.time())
	new_doc = Docs([doc_md, title, content, grade, genre, words, "", "", view, 0, 0, create_time, create_time, former_url, "攻略"])
	db.session.add(new_doc)
db.session.commit()
