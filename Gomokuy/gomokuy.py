#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from base import BaseGame, B, W, cost_count
from conf import a
from collections import Counter


SCORE = {
    "活5": 100000,
    "活4": 100000,
    "冲5": 10000,
    "冲4": 10000,
    "活3": 1000,
    "冲3": 100,
    "活2": 10,
    "冲2": 1,
    "活1": 1,
    "冲1": 1,
}


class Gomokuy(BaseGame):
    def __init__(self):
        BaseGame.__init__(self)
        self.values = {
            B: defaultdict(list),
            W: defaultdict(list),
        }
        self.lines = {
            B: [],
            W: [],
        }

    def __init_all_lines(self):
        for direction in range(4):
            checked = set([])
            for row in range(self.width):
                for col in range(self.width):
                    chess = self.table[row][col]
                    if not chess:
                        continue
                    if (row, col) in checked:
                        continue
                    line = self.base_linear(row, col, chess, direction)
                    checked |= set(line["s"])
                    if len(line["s"]) + len(line[-1]) + len(line[0]) + len(line[1]) < 5:
                        continue
                    self.lines[chess].append(line)

    def __refresh_new_lines(self):
        def remove_old_lines():
            if self.records:
                last = self.records[-1]
                for sid, d in self.values.items():
                    for k, lines in d.items():
                        new_lines = [line for line in lines if last not in line]
                        self.values[sid][k] = new_lines

        def add_new_lines():
            if not self.overdue_chess:
                return
            for loc, direction in self.overdue_chess:
                row, col = loc
                chess = self.table[row][col]
                line = self.base_linear(row, col, chess, direction)
                if len(line["s"]) + len(line[-1]) + len(line[0]) + len(line[1]) < 5:
                    continue
                self.fresh_lines[chess].append(line)
        remove_old_lines()
        add_new_lines()

    def __line_grouping(self, init_all=True):
        all_lines = self.lines if init_all else self.fresh_lines
        for sid, lines in all_lines.items():
            for line in lines:
                chang = min(5, len(line["s"] + line[0]))
                t = len(line["s"])
                t = "5" if t >= 5 else str(t)
                if line[-1] and line[1]:
                    key = "活" + t if len(line[0]) <= 1 else "冲" + t
                    range_att = min(max(0, 4 - chang), 2)
                    range_def = 1 if chang < 5 else 0
                    r = range_att if sid else range_def
                    line[-1] = line[-1][:r]
                    line[1] = line[1][:r]
                    format_line = line[-1] + line[0] + line[1]

                elif line[0] or line[1] or line[-1]:
                    key = "冲" + t
                    r = 5 - chang
                    line[-1] = line[-1][:r]
                    line[1] = line[1][:r]
                    format_line = line[-1] + line[0] + line[1]
                else:
                    continue
                self.values[sid][key].append(format_line)

    def analyse(self):
        def win_chance_single_line():
            best_lines = []

            if "冲4" in self_chance or "活4" in self_chance or "活5" in self_chance or "冲5" in self_chance:
                if player == B:
                    best_lines = self_chance["冲4"] + self_chance["活4"]
                else:
                    best_lines = self_chance["冲4"] + self_chance["活4"] + self_chance["冲5"] + self_chance["活5"]
            elif "冲4" in opponent_chance or "活4" in opponent_chance or "活5" in opponent_chance or "冲5" in opponent_chance:
                if player == W:
                    best_lines = opponent_chance["冲4"] + opponent_chance["活4"]
                else:
                    best_lines = opponent_chance["冲4"] + opponent_chance["活4"] + opponent_chance["冲5"] + opponent_chance["活5"]
            elif "活3" in self_chance:
                best_lines = self_chance["活3"]

            return list(set(sum(best_lines, [])))

        def win_chance_mul_lines():
            my_3 = sum(self_chance["活2"], [])
            my_4 = sum(self_chance["冲3"], [])
            your_live_3 = sum(opponent_chance["活3"], [])

            my_33 = [item[0] for item in Counter(my_3).items() if item[1] > 1]
            my_44 = [item[0] for item in Counter(my_4).items() if item[1] > 1]
            my_43 = [item for item in my_4 if item in my_3]

            if player == B:
                # 针对黑棋，自己的四三 > 对方的活三
                attack = [item for item in my_43 if item not in my_44 + my_33] or your_live_3
                # todo: 43不能在同一行，比如 0 1 1 1 0 0 1 0 0，此时电脑会判断中间两个0能够组成43胜，但是其实是长连禁手
            else:
                # 针对白棋，自己四四或四三 > 对方的活三 > 自己的三三，都没有实际上返回的是 False
                attack = my_44 + my_43 or your_live_3 or my_33

            if attack:
                ret = list(set(attack))
            else:
                # 假如没有进攻，就被迫开始防守
                your_3 = sum(opponent_chance["活2"], [])
                your_4 = sum(opponent_chance["冲3"], [])
                your_33 = [item[0] for item in Counter(your_3).items() if item[1] > 1]
                your_44 = [item[0] for item in Counter(your_4).items() if item[1] > 1]
                your_43 = [item for item in your_4 if item in your_3]
                if player == B:
                    fir = your_44 + your_43
                    sec = your_33 + my_4 + my_3
                else:
                    fir = [item for item in your_43 if item not in your_44 + your_33]
                    sec = your_33 + my_4 + my_3
                defence = fir if fir else sec
                ret = list(set(defence))
            return ret

        def normal_chance():
            # 从["冲3", "活2", "冲2", "冲1", "活1"]中选择
            temp = [i[j] for i in (self_chance, opponent_chance) for j in ("冲3", "活2", "冲2", "冲1", "活1")]
            ret = list(set(sum(sum(temp, []), [])))
            return ret

        player = B if (self.step + 1) % 2 == 1 else W
        opponent = W if player == B else B

        self_chance = self.values[player]
        opponent_chance = self.values[opponent]
        self.__refresh_new_lines()
        self.__line_grouping(init_all=False)

        return win_chance_single_line() or win_chance_mul_lines() or normal_chance()

    def min_max_search(self, DEEPS=5):
        def win_or_lose(deeps):
            next_player = B if (self.step + 1) % 2 == 1 else W
            opponent = W if next_player == B else B
            if not self.winner:
                if deeps == 0:
                    my_score = sum([SCORE[key] * len(v) for (key, v) in self.values[next_player].items()])
                    your_score = sum([SCORE[key] * len(v) for (key, v) in self.values[opponent].items()])
                    return my_score - your_score
                else:
                    poss = self.analyse()
                    if not poss:
                        return False
                    result = [0] * len(poss)
                    for ind, pos in enumerate(poss):
                        self.going(pos, show=False)
                        if deeps == DEEPS:
                            new_deeps = deeps - 1 if len(poss) > 1 else 0
                        else:
                            new_deeps = deeps - 1
                        temp_score = win_or_lose(new_deeps)
                        result[ind] = temp_score
                        self.undo()
                        if temp_score == 9999999 and next_player == my_roll:
                            # 轮到自己，且某一步可以自己赢
                            break
                        elif temp_score == -9999999 and next_player != my_roll:
                            # 轮到对方走，且某一步可以对方赢
                            break
                    if deeps == DEEPS:
                        return result, poss
                    elif next_player == my_roll:
                        return max(result)
                    else:
                        return min(result)
            elif self.winner == my_roll:
                return 9999999
            else:
                return -9999999

        if self.winner:
            return False
        self.values = {
            B: defaultdict(list),
            W: defaultdict(list),
        }
        self.lines = {
            B: [],
            W: [],
        }
        self.__init_all_lines()
        self.__line_grouping()
        my_roll = B if (self.step + 1) % 2 == 1 else W
        fin_result, fin_poss = win_or_lose(DEEPS)
        print(f"result=\t{fin_result}\nposs=\t{fin_poss}")
        print(f"best=\t{fin_poss[fin_result.index(max(fin_result))]}")
        return fin_poss[fin_result.index(max(fin_result))]


@cost_count
def bag():
    g = Gomokuy()
    g.parse(a)
    g.min_max_search(DEEPS=8)

if __name__ == '__main__':
    bag()
