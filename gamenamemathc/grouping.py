import os
from collections import Counter

long_game_name = ["占坑"]
short_game_name = []
namelist = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/userdict/gamename.txt"
flag = True
c = Counter()
with open(namelist, "r", encoding="utf-8") as txt111:
    for item in txt111:
        new_game = item.strip()
        for index, longer_name in enumerate(long_game_name):
            if longer_name.find(new_game) > -1:
                short_game_name.append(new_game)
                flag = False
                break
            if new_game.find(longer_name) > -1:
                long_game_name[index] = new_game
                short_game_name.append(longer_name)
                flag = False
                break
        if flag:
            long_game_name.append(new_game)
        flag = True

    for item in txt111:
        for i in item.strip():
            c[i] += 1

    print(c)


long_game_name.pop(0)
