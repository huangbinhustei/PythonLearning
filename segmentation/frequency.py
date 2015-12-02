import heapq
import os
stopwords = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))  + "/DATA/stopwords/stopwords_for_game_name.txt"

with open(stopwords, "r", encoding="utf-8") as txt111:
    go_away_top = txt111.read()


def top(loc, top=10):
    with open(loc, "r", encoding="utf-8") as txt:
        contain = txt.readlines()

    count = []
    sku_top = []
    for row in contain:
        for cell in row.strip():
            if go_away_top.count(cell) != 0:
                continue
            if sku_top.count(cell) == 0:
                sku_top.append(cell)
                count.append(1)
            else:
                count[sku_top.index(cell)] += 1

    next_final = list(map(lambda x, y: [x, y], sku_top, count))
    for_print = sorted(next_final, key=lambda a: a[1], reverse=True)
    return for_print[:top]


go_away_next = ",.!?<>() []{}，。！？《》（）\n"


def find_next(loc, str_group, top=10):
    with open(loc, "r", encoding="utf-8") as txt:
        contain = txt.read().strip("")
        count_next = []
        sku_next = []
        target = str_group
        while contain.count(target) > 0:
            idx = contain.index(target)
            contain = contain[idx + len(target):]
            this_next = contain[:1]
            if go_away_next.count(this_next) != 0:
                continue
            if sku_next.count(this_next) == 0:
                sku_next.append(this_next)
                count_next.append(1)
            else:
                count_next[sku_next.index(this_next)] += 1

        next_final = list(map(lambda x, y: [x, y], sku_next, count_next))
        return heapq.nlargest(top, next_final, lambda t: t[1])
