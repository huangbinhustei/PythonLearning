import xlrd
game_name=[]
needxx = []
x2pop = 0
result = []

with open("gamename.txt", "r", encoding="utf-8") as txt111:
	for item in txt111.readlines():
		game_name.append(item.strip())


# for i in range(len(game_name)-1):
# 	for j in range(i+1,len(game_name)):
# 		if i == j:
# 			continue
# 		if game_name[i].find(game_name[j])>-1:
# 			needxx.append(j)
# 		elif game_name[j].find(game_name[i])>-1:
# 			needxx.append(i)


# for idx in needxx:
# 	game_name.pop(idx-x2pop)
# 	x2pop +=1


with xlrd.open_workbook("titlelist.xlsx") as data:
	table = data.sheets()[0]
	for i in range(table.nrows):
		doc_title = table.cell(i,0).value
		count = 0
		temp = " "
		for name in game_name:
			if doc_title.find(name) > -1:
				temp = name
				count +=1
		if count == 1:
			result.append([doc_title,temp,table.cell(i,2).value,table.cell(i,3).value])
		elif count > 1:
			result.append([doc_title,count,table.cell(i,2).value,table.cell(i,3).value])


with open("result.txt", "w", encoding="gbk") as f:
	for witem in result:
		abdfd = str(witem[0])+"\t"+str(witem[1])+"\t"+str(int(witem[2]))+"\t"+str(witem[3])+"\n"
		f.write(abdfd)