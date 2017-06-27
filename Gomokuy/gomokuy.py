#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from base import BaseGame, B, W
from conf import a, SCORE, cost_count
from random import choice
from functools import reduce
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
                    line = self.inside_make_line_for_single(row, col, chess, direction, line)
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
                if line[-1] and line[1]:
                    if len(line[0]) <= 1:
                        key = "活" + str(len(line["s"]))
                    else:
                        key = "冲" + str(len(line["s"]))
                    range_att = max(0, 4 - chang)
                    range_def = 1 if chang < 5 else 0
                    r = range_att if sid else range_def
                    line[-1] = line[-1][:r]
                    line[1] = line[1][:r]

                elif line[0] or line[1] or line[-1]:
                    key = "冲" + str(len(line["s"]))
                    r = 5 - chang
                    line[-1] = line[-1][:r]
                    line[1] = line[1][:r]
                else:
                    continue
                self.values[sid][key].append(line)

    # @cost_count
    def analyse(self, single_step=True):
        def make_pos_group():
            me = B if (self.step + 1) % 2 == 1 else W

            my_lines_three = [sum([line[0], line[1], line[-1]], []) for line in self_chance["活2"]]
            my_lines_four = [sum([line[0], line[1], line[-1]], []) for line in self_chance["冲3"]]
            your_live_three = [sum([line[0], line[1], line[-1]], []) for line in opponent_chance["活3"]]
            your_lines_three = [sum([line[0], line[1], line[-1]], []) for line in opponent_chance["活2"]]
            your_lines_four = [sum([line[0], line[1], line[-1]], []) for line in opponent_chance["冲3"]]

            my_33 = [item[0] for item in Counter(sum(my_lines_three, [])).items() if item[1] > 1]
            my_44 = [item[0] for item in Counter(sum(my_lines_four, [])).items() if item[1] > 1]
            my_43 = [item[0] for item in
                     Counter(list(set(sum(my_lines_four, []))) + list(set(sum(my_lines_three, [])))).items() if
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
                        return sum(your_live_three, [])
                    else:
                        # 正常进攻
                        attack = sum(my_lines_four + my_lines_three, [])
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
                        return sum(your_live_three, [])
                    else:
                        # 如果对方没有活3，自己有33就进攻，没有33就正常进攻
                        attack = my_33 if my_33 else sum(my_lines_four + my_lines_three, [])
                        if attack:
                            return attack

            # 假如没有进攻，就被迫开始防守
            your_33 = [item[0] for item in Counter(sum(your_lines_three, [])).items() if item[1] > 1]
            your_44 = [item[0] for item in Counter(sum(your_lines_four, [])).items() if item[1] > 1]
            your_43 = [item[0] for item in
                       Counter(list(set(sum(your_lines_four, []))) + list(set(sum(your_lines_three, [])))).items()
                       if item[1] > 1]
            defence = your_33 + your_44 + your_43 if me == B else [item for item in your_43 if
                                                                   item not in your_44 + your_33]
            if not defence:
                defence = sum(your_lines_three + your_lines_four, [])
            return defence

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
        # print(self_chance)
        opponent_chance = self.values[False]
        if "冲4" in self_chance or "活4" in self_chance:
            best_lines = self_chance["冲4"] + self_chance["活4"]
        elif "冲4" in opponent_chance or "活4" in opponent_chance:
            best_lines = opponent_chance["冲4"] + opponent_chance["活4"]
        elif "活3" in self_chance:
            best_lines = self_chance["活3"]
        else:
            best_lines = False
        if best_lines:
            best_pos_group = sum([d[0] + d[1] + d[-1] for d in best_lines], [])
            best_pos_group = list(set(best_pos_group))
        else:
            best_pos_group = make_pos_group()
            if not best_pos_group:
                # 从["冲2", "活1", "冲1"]中选择
                best_pos_group = [sum([line[0], line[1], line[-1]], []) for line in self_chance["冲2"]] + [
                    sum([line[0], line[1], line[-1]], []) for line in self_chance["冲1"]] + [
                                     sum([line[0], line[1], line[-1]], []) for line in self_chance["活1"]] + [
                                     sum([line[0], line[1], line[-1]], []) for line in opponent_chance["冲2"]] + [
                                     sum([line[0], line[1], line[-1]], []) for line in opponent_chance["冲1"]] + [
                                     sum([line[0], line[1], line[-1]], []) for line in opponent_chance["活1"]]
                best_pos_group = sum(best_pos_group, [])

        single = choice(best_pos_group)
        mul = best_pos_group
        ret = single if single_step else mul
        return ret

    def temp(self, me, deeps):
        def logging(_pos, _deeps):
            if _deeps == DEEPS:
                print(f"\nThe first step is {_pos}")

        if not self.winner:
            if deeps == 0:
                print(self.records)
                return 0
            else:
                poss = self.analyse(single_step=False)
                result = [0] * len(poss)
                for ind, pos in enumerate(poss):
                    logging(pos, deeps)
                    self.going(pos)
                    temp_score = self.temp(me, deeps - 1)
                    result[ind] = temp_score
                    self.ungoing()
                    next_player = B if (self.step + 1) % 2 == 1 else W
                    if temp_score == 1 and next_player == me:
                        # 轮到自己，且某一步可以自己赢
                        break
                    elif temp_score == -1 and next_player != me:
                        # 轮到对方走，且某一步可以对方赢
                        # 这里剪枝有问题，禁手不算，并且禁手明明是黑棋自己走出的，不应该出现剪刀
                        pass
                        # break
                if deeps == DEEPS:
                    print(poss)
                    return result
                elif deeps % 2 == 0:
                    return max(result)
                else:
                    return min(result)
        elif self.winner == me:
            return 1
        else:
            return -1

    @cost_count
    def mul(self):
        me = B if (self.step + 1) % 2 == 1 else W
        print(self.temp(me, DEEPS))


if __name__ == '__main__':
    DEEPS = 8
    g = Gomokuy()
    g.parse(a)
    g.mul()
    # print(g.analyse(single_step=False))
    # print(g._ending((7, 3), B))
