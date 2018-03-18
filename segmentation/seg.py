import re
import os
import time
import logging
import math
import sys
from collections import defaultdict
from multiprocessing import Pool

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
base = os.path.abspath(os.path.dirname(__file__))


class ProgressBar:
    def __init__(self, count=0, total=0, width=50):
        self.count = count
        self.total = total
        self.width = width

    def move(self):
        self.count += 1
        sys.stdout.write(' ' * (self.width + 9) + '\r')
        sys.stdout.flush()
        progress = int(self.width * self.count / self.total)
        sys.stdout.write('{0:3}/{1:3}: '.format(self.count, self.total))
        sys.stdout.write('+' * progress + '-' * (self.width - progress) + '\r')
        if progress == self.width:
            sys.stdout.write('\n')
        sys.stdout.flush()


class SEG:
    def __init__(self, cont, title="default", max_length=10, stops=""):
        self.start = time.time()

        self.title = title
        self.cont = cont
        self.line = ""  # 将文章合并为单行
        self.size = 0
        # 以上四个是文章的属性

        self.stops = stops
        self.max_length = max_length
        self.door = int(self.size / 10000) + 3

        self.word = {
            "candidates": defaultdict(int),
            "book": defaultdict(int),
        }

        self.en = defaultdict(int)
        self.phrase = defaultdict(int)

        self.not_word = set([])
        self.neighbor = dict()

        self.__screening()

    def __screening(self):
        """
        对文本进行预处理，包括：
        1. 提取所有成对书名号中的内容，存入 self.word["book"]
        2. 将所有标点符号，替换为 $
        3. 处理后的文章合并为一行
        4. 计算文章总长度
        5. 将文章组成词对
        """

        def booker():
            book_mark = re.compile("《.+?》")
            for line in self.cont:
                for item in re.findall(book_mark, line):
                    self.word["book"][item] += 1

        def englisher():
            zp = re.compile(u'[\u4e00-\u9fa5]+')
            tmp = []
            for line in self.cont:
                if not zp.search(line):
                    self.en[line] += 1
                else:
                    tmp.append(line)
            self.cont = tmp

        def punctuationer():
            self.cont = [re.sub(punctuation, "$", line) for line in self.cont if line]  # 除书名号外，其他符号被处理成$
            self.line = "$" + "$".join(self.cont) + "$"
            self.size = len(self.line)

        def phraser():
            def grouping(extent):
                for line in self.cont:
                    if len(line) <= extent:
                        # 为什么是 continue？
                        continue
                    for cell in [line[i:i + extent + 1] for i in range(len(line) - extent)]:
                        self.phrase[cell] += 1
                        if re.findall(punctuation, cell):
                            self.not_word.add(cell)

            for i in range(self.max_length):
                grouping(i)

        punctuation = re.compile("[（）、.，。 ？！：；$“”…‘’ \t\n]")
        booker()
        englisher()
        punctuationer()
        phraser()

    def _show_top_tf(self):

        print("+-%-24s-+-%-6s-+-%-6s-+" % ("-" * 24, "-" * 6, "-" * 6))
        space_title = ' ' * (25 - 2 * len(self.title) - 11)
        print(f"| Keywords @ {self.title}{space_title}| {' '*4}TF | {' '*3}PMI |")
        print("+-%-24s-+-%-6s-+-%-6s-+" % ("-" * 24, "-" * 6, "-" * 6))
        for w, freq in sorted(self.word["candidates"].items(), key=lambda x: x[1], reverse=True)[:10]:
            space_fi = ' ' * (25 - 2 * len(w))
            space_sec = ' ' * (6 - len(str(freq)))
            w_pmi = round(self.filtering_pmi(w, freq), 3)
            space_thi = ' ' * (6 - len(str(w_pmi)))
            print(f"| {w}{space_fi}| {space_sec}{freq} | {space_thi}{w_pmi} |{self.neighbor[w]}")
        print("+-%-24s-+-%-6s-+-%-6s-+" % ("-" * 24, "-" * 6, "-" * 6))

    def _neighbourhood_for_single_word(self, word):
        # todo :word 太长的时候，下面的算法不对

        left = defaultdict(int)
        right = defaultdict(int)

        par = re.compile('.' + word + '.')
        for item in re.findall(par, self.line):
            left[item[0]] += 1
            right[item[-1]] += 1

        freq_left = [v for k, v in left.items()]
        total_left = sum(freq_left)
        freq_left = [v / total_left for v in freq_left]
        freq_right = [v for k, v in right.items()]
        total_right = sum(freq_right)
        freq_right = [v / total_right for v in freq_right]

        ret = [
            int(sum([-i * math.log(i) for i in freq_left]) * 100),
            int(sum([-i * math.log(i) for i in freq_right]) * 100)
        ]
        if max(ret) <= 100:
            self.not_word.add(word)

        return ret

    def filtering_neighbourhood(self):
        for word, freq in self.phrase.items():
            if word in self.not_word:
                continue
            elif freq < self.door:
                continue
            self.neighbor[word] = self._neighbourhood_for_single_word(word)

    def filtering_bayesian(self, word, prob_ab):
        word_length = len(word)

        sub_words = [word[i: j] for i in range(word_length) for j in range(word_length + 1) if j > i]
        sub_words.remove(word)

        for sub_word in sub_words:
            prob_b = self.phrase[sub_word]
            if len(sub_word) == 1:
                self.not_word.add(sub_word)
                # 一个字的都不算词。
                continue
            if prob_ab / prob_b > 0.5:
                # 相当于 P(A|B) = P(AB)/P(B) > 50%，只要 B 出现那么 AB 肯定出现 => B 肯定不是词
                self.not_word.add(sub_word)

    def filtering_unnamed(self, word, prob_ab):
        dangers = []
        for i in range(len(word) - 1):
            dangers.append(min(self.phrase[word[:i + 1]], self.phrase[word[i + 1:]]))
        prob_danger = max(dangers)
        if prob_ab / prob_danger <= 0.5:
            # 假如父比某个子对的出现概率小太多，那么父词可能不是词
            self.not_word.add(word)

    def filtering_pmi(self, word, prob_ab):
        prob_danger = 1
        for i in range(len(word) - 1):
            prob_danger = max(self.phrase[word[:i + 1]] * self.phrase[word[i + 1:]], prob_danger)
        ret = prob_danger / prob_ab / self.size
        if ret > 0.02:
            self.not_word.add(word)
        return ret

    def run(self):
        for word in sorted(self.phrase.keys(), key=lambda x: len(x), reverse=True):
            if word in self.not_word or len(word) == 1 or self.phrase[word] < self.door:
                continue
            prob_ab = self.phrase[word]

            self.filtering_bayesian(word, prob_ab)
            if len(word) == 2 and word[0] == word[1]:
                # todo: 叠字在后面两个的处理中非常吃亏，临时过滤掉
                continue
            self.filtering_unnamed(word, prob_ab)
            self.filtering_pmi(word, prob_ab)
            # todo: PMI 没有提供任何有价值的筛选

        self.filtering_neighbourhood()

        for word, freq in self.phrase.items():
            if word in self.not_word:
                continue
            elif len(word) == 1:
                continue
            elif word in self.stops:
                continue
            self.word["candidates"][word] = freq

        # self._show_top_tf()


class Book(ProgressBar):
    def __init__(self, name, paths):
        self.name = name
        self.paths = paths
        self.stops = ""

        ProgressBar.__init__(self, total=len(paths))

        self.result = []
        self.idf = defaultdict(int)

    def _record(self):
        with open(os.path.join(base, "doc", self.name + "IDF.txt"), "w") as f:
            for k, v in self.idf.items():
                f.write(f"{v}\t{k}\n")

    def _show(self):
        def rank_key(f):
            return f[1] * math.log(120 / self.idf[f[0]], 120)

        for chapter, title in self.result:
            for w, freq in sorted(chapter["candidates"].items(), key=rank_key, reverse=True)[:10]:
                print(f"{freq}\t{self.idf[w]}\t{w}\t{title}\t")

    def run(self):
        for file, title in self.paths:
            chapter = SEG(get_content(file), title, stops="")
            chapter.run()

            self.result.append([chapter.word, title])

            for key, freq in chapter.word["candidates"].items():
                self.idf[key] += 1

            self.move()

        self._record()
        self._show()


def get_content(path):
    with open(path, "r", encoding="utf-8") as f:
        ret = [line.strip() for line in f.readlines()]
    return ret


def load_stop_words():
    with open(os.path.join(base, "doc", "stop_word.txt"), "r") as f:
        return [item.strip() for item in f.readlines()]


def red_dream():
    folder = os.path.join(base, "doc", "红楼梦")
    _, _, files = next(os.walk(folder))
    tasks = [[os.path.join(folder, i), i.replace(".txt", "")] for i in files if i[-3:] == "txt"]

    red = Book("红楼梦", tasks)
    red.run()


if __name__ == '__main__':
    t = time.time()
    red_dream()
    print("任务完成：" + str(int((time.time() - t) * 1000)) + " ms")
