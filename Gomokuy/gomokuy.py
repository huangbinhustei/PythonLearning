#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from base import BaseGame, B, W
from conf import a, SCORE, cost_count
from random import choice
from collections import Counter


class Gomokuy(BaseGame):
    def __init__(self):
        BaseGame.__init__(self)
        self.values = dict()
        self.lines = {
            True: [],
            False: [],
        }

    def inside_make_line(self):
        for direction in range(4):
            checked = set([])
            for row in range(self.width):
                for col in range(self.width):
                    chess = self.table[row][col]
                    if not chess:
                        continue
                    if (row, col) in checked:
                        continue
                    line = {
                        "s": [(row, col)],
                        0: [],  # 中间的缝隙
                        -1: [],  # 某一边的空
                        1: [],  # 另一边的空
                    }
                    line = self.base_linear(row, col, chess, direction, line)
                    self.inside_line_filter(line, chess)
                    checked |= set(line["s"])

    def inside_line_filter(self, line, chess):
        me = B if (self.step + 1) % 2 == 1 else W
        if len(line["s"]) + len(line[-1]) + len(line[0]) + len(line[1]) < 5:
            return
        self.lines[chess == me].append(line)

    def inside_line_grouping(self):
        for sid, lines in self.lines.items():
            for line in lines:
                chang = min(5, len(line["s"] + line[0]))
                t = len(line["s"]) 
                t = "5" if t >= 5 else str(t)
                if line[-1] and line[1]:
                    if len(line[0]) <= 1:
                        key = "活" + t
                    else:
                        key = "冲" + t
                    range_att = max(0, 4 - chang)
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

    # @cost_count
    def analyse(self, single_step=True):
        def make_pos_group():
            my_lines_three = sum(self_chance["活2"], [])
            my_lines_four = sum(self_chance["冲3"], [])

            your_live_three = sum(opponent_chance["活3"], [])
            your_lines_three = sum(opponent_chance["活2"], [])
            your_lines_four = sum(opponent_chance["冲3"], [])

            my_33 = [item[0] for item in Counter(my_lines_three).items() if item[1] > 1]
            my_44 = [item[0] for item in Counter(my_lines_four).items() if item[1] > 1]
            my_43 = [item[0] for item in
                     Counter(list(set(my_lines_four)) + list(set(my_lines_three))).items() if
                     item[1] > 1]

            if me == B:
                # 针对黑棋
                attack = [item for item in my_43 if item not in my_44 + my_33]
                if attack:
                    return attack
                    # 如果有43，直接进攻
                else:
                    if your_live_three:
                        # 如果没有43， 对方有活3，只能防守
                        return your_live_three
                    else:
                        # 正常进攻
                        attack = my_lines_four + my_lines_three
                        if attack:
                            return attack
            else:
                # 针对白棋
                attack = my_44 + my_43
                if attack:
                    # 如果有44或43，直接进攻
                    return attack
                else:
                    if your_live_three:
                        # 如果没有43, 43， 对方有活3，只能防守
                        return your_live_three
                    else:
                        # 如果对方没有活3，自己有33就进攻，没有33就正常进攻
                        attack = my_33 if my_33 else my_lines_four + my_lines_three
                        if attack:
                            return attack

            # 假如没有进攻，就被迫开始防守
            your_33 = [item[0] for item in Counter(your_lines_three).items() if item[1] > 1]
            your_44 = [item[0] for item in Counter(your_lines_four).items() if item[1] > 1]
            your_43 = [item[0] for item in
                       Counter(list(set(your_lines_four)) + list(set(your_lines_three))).items()
                       if item[1] > 1]
            defence = your_33 + your_44 + your_43 if me == B else [item for item in your_43 if
                                                                   item not in your_44 + your_33]
            if not defence:
                defence = your_lines_three + your_lines_four
            return defence

        me = B if (self.step + 1) % 2 == 1 else W
        self.values = {
            True: defaultdict(list),
            False: defaultdict(list),
        }
        self.lines = {
            True: [],
            False: [],
        }
        self.inside_make_line()
        self.inside_line_grouping()

        self_chance = self.values[True]
        opponent_chance = self.values[False]
        if "冲4" in self_chance or "活4" in self_chance:
            if me == B:
                best_lines = self_chance["冲4"] + self_chance["活4"]
            else:
                best_lines = self_chance["冲4"] + self_chance["活4"] + self_chance["冲5"] + self_chance["活5"]
        elif "冲4" in opponent_chance or "活4" in opponent_chance:
            best_lines = opponent_chance["冲4"] + opponent_chance["活4"]
        elif "活3" in self_chance:
            best_lines = self_chance["活3"]
        else:
            best_lines = False
        if best_lines:
            best_pos_group = sum(best_lines, [])
            best_pos_group = list(set(best_pos_group))
        else:
            best_pos_group = make_pos_group()
            if not best_pos_group:
                # 从["冲2", "活1", "冲1"]中选择
                temp = [self_chance[k] for k in ["冲2", "冲1", "活1"]] + [opponent_chance[k] for k in ["冲2", "冲1", "活1"]]
                best_pos_group = list(set(sum(sum(temp, []), [])))

        single = choice(best_pos_group)
        mul = best_pos_group
        ret = single if single_step else mul
        return ret

    @cost_count
    def min_max_search(self, DEEPS=5):
        def logging(_pos, _deeps):
            if _deeps == DEEPS:
                print(f"The first step is {_pos}")

        def win_or_lose(deeps):
            if not self.winner:
                if deeps == 0:
                    my_score = sum([SCORE[key] * len(v) for (key, v) in self.values[True].items()])
                    your_score = sum([SCORE[key] * len(v) for (key, v) in self.values[False].items()])
                    return my_score - your_score
                else:
                    poss = self.analyse(single_step=False)
                    if not poss:
                        return False
                    # if len(poss) == 1:
                    #     return 0, poss[0]
                    result = [0] * len(poss)
                    next_player = B if (self.step + 1) % 2 == 1 else W
                    for ind, pos in enumerate(poss):
                        logging(pos, deeps)
                        self.going(pos)
                        temp_score = win_or_lose(deeps - 1)
                        result[ind] = temp_score
                        self.fallback()
                        if temp_score == 1 and next_player == me:
                            # 轮到自己，且某一步可以自己赢
                            break
                        elif temp_score == -1 and next_player != me:
                            # 轮到对方走，且某一步可以对方赢
                            break
                    if deeps == DEEPS:
                        return result, poss
                    elif next_player == me:
                        return max(result)
                    else:
                        return min(result)
            elif self.winner == me:
                return 1000000
            else:
                return -1000000

        if self.winner:
            return False
        me = B if (self.step + 1) % 2 == 1 else W 
        fin_result, fin_poss = win_or_lose(DEEPS)
        print(f"result=\t{fin_result}\nposs=\t{fin_poss}")
        print(f"best=\t{fin_poss[fin_result.index(max(fin_result))]}")
        return fin_poss[fin_result.index(max(fin_result))]


if __name__ == '__main__':
    g = Gomokuy()
    g.parse(a)
    g.min_max_search(DEEPS=5)
    # print(g.analyse(single_step=False))
    # print(g._ending((7, 3), B))
