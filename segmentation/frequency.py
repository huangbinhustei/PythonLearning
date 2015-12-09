import heapq
import os
import string
from contextlib import closing
from collections import defaultdict

stopwords = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/stopwords/stopwords_for_game_name.txt"

with open(stopwords, "r", encoding="utf-8") as txt111:
    go_away_top = txt111.read()
    stop_words = set(go_away_top)

go_away_next = ",.!?<>() []{}，。！？《》（）-_+-*、—\n/n第的了关升"


def top(loc, medal=10):
    counter = defaultdict(lambda: 0)
    for line in loc:
        for cell in line.strip():
            if cell in stop_words:
                continue
            counter[cell] += 1
    temp1 = dict((k, v) for k, v in counter.items() if v > medal)
    temp = heapq.nlargest(len(counter), temp1.items(), lambda x: x[1])
    return temp


def find_next(loc, str_group, medal2=10, reverse=False):
    counts = defaultdict(lambda: 0)
    target = str_group
    with open(loc, "r", encoding="utf-8") as txt:
    # with open(loc, "r", encoding="gbk") as txt:
        contain = txt.read().strip()
        cc = list(contain.split(target))
        if reverse:
            dd = map(lambda t: t[-1:], cc)
        else:
            dd = map(lambda t: t[:1], cc)  # 取第一个字符
        for this_next in dd:
            if go_away_next.count(this_next) != 0:
                continue
            counts[this_next] += 1
    return heapq.nlargest(medal2, counts.items(), lambda x: x[1])
