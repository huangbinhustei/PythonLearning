import re
import os
import time
import logging
from collections import defaultdict
from threading import Thread

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MyThread(Thread):
    # 做这个是为了 get_result
    def __init__(self, article, stops_config):
        Thread.__init__(self)
        self.article = article
        self.stops_config = stops_config
        self.result = None

    def run(self):
        self.result = cutting(self.article, self.stops_config)

    def get_result(self):
        return self.result


class SEG:
    def __init__(self, path, title="default", max_length=10, stops=""):
        self.title = "《" + title + "》"
        self.start = time.time()

        par = re.compile("[:，.、。 ？！；：“”…‘’]")
        with open(path, "r", encoding="utf-8") as f:
            cont = [re.sub(par, "\t", line.strip()) for line in f.readlines()]
            self.cont = sum([i.split("\t") for i in cont], [])

        self.no_use_singles = "这那一二三四五六七八九十百千万里众在都全两双对个钱银的是把被若又才好坏还怎天日曰说回知只有没不儿个了着子女东西物样进出来去入过回之乎者也"
        # self.no_use_singles = ""
        self.stops = stops
        self.max_length = max_length
        self.door = int(len(",".join(self.cont)) / 100000) + 1
        print(f"{self.title}加载完成，阈值 {self.door}，开始分析@{time.ctime()}")

        self.en = defaultdict(int)
        self.zh = defaultdict(int)
        self.book = defaultdict(int)
        self.result = dict()

    def booker(self):
        book_mark = re.compile("《.+?》")
        for item in re.findall(book_mark, " ".join(self.cont)):
            self.book[item] += 1
        # print(self.book)

    def filter(self):
        zp = re.compile(u'[\u4e00-\u9fa5]+')
        tmp = []

        for item in self.cont:
            if not item:
                continue
            elif not zp.search(item):
                # 不包含中文
                self.en[item] += 1
            else:
                tmp.append(item)
        self.cont = tmp

    def grouping(self, lth):
        tmp = defaultdict(int)
        for line in self.cont:
            if len(line) <= lth:
                continue
            for cell in [line[i:i + lth + 1] for i in range(len(line) - lth)]:
                tmp[cell] += 1
        for k, v in tmp.items():
            if v >= self.door:
                self.zh[k] += v

    def run(self):
        self.booker()
        self.filter()

        for i in range(self.max_length):
            self.grouping(i)

        jmp = set([])
        for word in sorted(self.zh.keys(), key=lambda x: len(x), reverse=True):
            if word in jmp or len(word) <= 2:
                continue

            word_length = len(word)
            p_word = self.zh[word]

            sub_words = [word[i: j] for i in range(word_length) for j in range(word_length + 1) if j > i]
            sub_words.remove(word)

            for sub_word in sub_words:
                if p_word / self.zh[sub_word] > 0.5:
                    # p(n字对|子对）< 0.5 => 子对不是词
                    jmp.add(sub_word)

            dangers = []
            for i in range(len(word) - 1):
                dangers.append(min(self.zh[word[:i + 1]], self.zh[word[i + 1:]]))
            p_danger = max(dangers)
            if p_word / p_danger < 0.5:
                # 假如父比最长子的出现概率小太多，那么父词可能不是词
                jmp.add(word)

        for k, v in self.zh.items():
            if k not in jmp and len(k) != 1 and k not in self.stops:
                rate = 0
                for ch in k:
                    if ch in self.no_use_singles:
                        # 整体来说是个诡异的策略
                        rate += 1
                if rate == len(k):
                    continue
                self.result[k] = v / pow(4, rate)

        for w, rate in sorted(self.result.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"{self.title}：\t{self.zh[w]}\t{int(rate)}\t{int(self.zh[w]//rate)}\t{w}")
        print(f"{self.title}分析完成@{time.ctime()}，耗时{int((time.time()-self.start)*1000)}ms")


def cutting(title, _stops):
    file = os.path.join(base, "doc", title + ".txt")
    s = SEG(file, title=title, stops=_stops)
    s.run()
    return s.result


def load_stop_words():
    with open(os.path.join(base, "doc", "stop_word.txt"), "r") as f:
        return [item.strip() for item in f.readlines()]


if __name__ == '__main__':
    symbols = "-_——+=*/，。？！,.!?\n\t 、:：《》<>\"\';；“”‘’……^"
    chi_symbols = ":，.、。《》？！；：“”……‘’"

    base = os.path.abspath(os.path.dirname(__file__))
    stops_config = load_stop_words()

    p = []
    res = []
    for article in ["红楼梦", "三国演义", "水浒传"]:
        p.append(MyThread(article, stops_config))
    for i in p:
        i.start()
    for i in p:
        i.join()
        res.append(i.get_result())




