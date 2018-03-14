import re
import os
import time
import logging
import math
from collections import defaultdict
from multiprocessing import Pool

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
base = os.path.abspath(os.path.dirname(__file__))


class SEG:
    def __init__(self, cont, title="default", max_length=10, stops=""):
        self.title = "《" + title + "》"
        self.start = time.time()
        self.cont = cont
        self.stops = stops
        self.max_length = max_length
        self.door = int(len(",".join(self.cont)) / 100000) + 2
        self.en = defaultdict(int)
        self.zh = defaultdict(int)
        self.book = defaultdict(int)
        self.result = dict()
        self.not_word = set([])

        print(f"{self.title}加载完成，阈值 {self.door}，开始分析@{time.ctime()}")

    def booker(self):
        book_mark = re.compile("《.+?》")
        for ind, line in enumerate(self.cont):
            for item in re.findall(book_mark, line):
                self.book[item] += 1
            self.cont[ind] = re.sub(book_mark, "\t", line)

    def filter(self):
        zp = re.compile(u'[\u4e00-\u9fa5]+')
        par = re.compile("[()（）:，.、。 ？！；：“”…‘’]")
        tmp = []

        cont = [re.sub(par, "\t", line) for line in self.cont]
        self.cont = sum([i.split("\t") for i in cont], [])

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
            if p_word / p_danger <= 0.5:
                # 假如父比某个子对的出现概率小太多，那么父词可能不是词
                jmp.add(word)

        self.not_word = set([i for i in jmp if len(i) >= 2])

        for k, v in self.zh.items():
            if k not in jmp and len(k) != 1 and k not in self.stops:
                self.result[k] = v
        

        # for w, rate in sorted(self.result.items(), key=lambda x: x[1], reverse=True)[:10]:
            # print(f"{self.title}：\t{self.zh[w]}\t{int(rate)}\t{int(self.zh[w]//rate)}\t{w}")
        print(f"{self.title}分析完成@{time.ctime()}，耗时{int((time.time()-self.start)*1000)}ms")

        
def get_content(path):
    ret = []
    with open(path, "r", encoding="utf-8") as f:
        ret = [line.strip() for line in f.readlines()]
    return ret


def cutting(content, title, _stops):
    s = SEG(cont=content, title=title, stops=_stops)
    s.run()
    return s.result, s.not_word


def load_stop_words():
    with open(os.path.join(base, "doc", "stop_word.txt"), "r") as f:
        return [item.strip() for item in f.readlines()]


def single_hander(paths,  _stops):
    ret = []
    idf = defaultdict(int)
    tf = defaultdict(int)
    neg = defaultdict(int)
    for file, title in paths:
        article = get_content(file)
        tf, _neg = cutting(article, title, _stops)

        for key, freq in tf.items():
            idf[key] += 1
            tf[key] += freq
        for key in _neg:
            neg[key] += 1

        ret.append([title, tf])

    final_idf = dict()
    for k, v in idf.items():
        if k not in neg or v >= neg[k]:
            final_idf[k] = v

    finnal_neg = dict()
    for k, v in neg.items():
        if k not in idf or v >= idf[k]:
            finnal_neg[k] = v 

    with open(os.path.join(base, "doc", "红楼梦IDF.txt"), "w") as f:
        for k, v in final_idf.items():
            # _tmp = []
            # for sk in final_idf.keys():
            #     if sk in k and sk != k:
            #         _tmp.append(sk)
            #     _p = "\t".join(_tmp)
            # f.write(f"{v}\t{k}\t{_p}\n")
            f.write(f"{v}\t{k}\n")


    with open(os.path.join(base, "doc", "红楼梦NEG.txt"), "w") as f:
        for k, v in finnal_neg.items():
            f.write(f"{v}\t{k}\n")

    def xu(arg):
        word, freq = arg
        if word not in neg or freq >= neg[word]:
            if idf[word] == 1:
                return freq * math.log(120/idf[word]) / 2
            return freq * math.log(120/idf[word])
        return 0

    for title, d in ret:
        for w, rate in sorted(d.items(), key=xu, reverse=True)[:10]:
            print(f"{title}\t{int(d[w])}\t{idf[w]}\t{w}")


def mult_hander(mult, _stops):
    p = Pool(min(3, len(mult)))
    for book, title in mult:
        p.apply_async(single_hander, args=([book, title], ""))
    p.close()
    p.join()


def red_dream():
    folder = os.path.join(base, "doc", "红楼梦")
    _, _, files = next(os.walk(folder))
    tasks = [[os.path.join(folder, i), i.replace(".txt", "")] for i in files if i[-3:] == "txt"]
    single_hander(tasks, "")


if __name__ == '__main__':
    symbols = "-_——+=*/，。？！,.!?\n\t 、:：《》<>\"\';；“”‘’……^"
    chi_symbols = ":，.、。《》？！；：“”……‘’"

    # ns = [["红楼梦"], ["三国演义"], ["水浒传"]]
    ns = [[os.path.join(base, "doc", i + ".txt"), i] for i in ["红楼梦", "三国演义", "水浒传"]]
    
    t = time.time()
    red_dream()
    # mult_hander(ns, load_stop_words())
    print(time.time()-t)
