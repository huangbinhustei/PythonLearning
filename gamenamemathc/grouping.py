game_name=[]
long_game_name = []
short_game_name = []

with open("游戏名称.txt", "r", encoding="utf-8") as txt111:
	for item in txt111.readlines():
		game_name.append(item.strip())


for i in range(len(game_name)-1):
	for j in range(i+1,len(game_name)):
		if i == j:
			continue
		if game_name[i].find(game_name[j])>-1:
			needxx.append(j)
		elif game_name[j].find(game_name[i])>-1:
			needxx.append(i)

x2pop = 0
for idx in needxx:
	game_name.pop(idx-x2pop)
	x2pop +=1

with open("gamename.txt", "w", encoding="utf-8") as f:
	for item in game_name:
		f.write(item)
		f.write("\n")
