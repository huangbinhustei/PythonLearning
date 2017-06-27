#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from base import BaseGame, B, W
from conf import a, SCORE, cost_count
from random import choice


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
        def make_pos_group(key_group):
            key_group = set([k for k in key_group])
            attack = sum([self_chance[k] for k in key_group], [])
            defence = sum([opponent_chance[k] for k in key_group], [])
            return attack if attack else defence

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

        me = B if (self.step + 1) % 2 == 1 else W
        self_chance = self.values[True]
        opponent_chance = self.values[False]
        if "冲4" in self_chance:
            best_lines = self_chance["冲4"]
        elif "冲4" in opponent_chance:
            best_lines = opponent_chance["冲4"]
        elif "活3" in self_chance:
            best_lines = self_chance["活3"]
        elif "活3" in opponent_chance:
            best_lines = self_chance["冲3"]
            best_lines += opponent_chance["活3"]
        else:
            temp_1 = make_pos_group(["活2", "冲3"])
            # 这里寻找交点，有机会赢
            best_lines = temp_1 if temp_1 else make_pos_group(["冲2", "活1", "冲1"])

        best_pos_group = sum([d[0] + d[1] + d[-1] for d in best_lines], [])
        best_pos_group = list(set(best_pos_group))
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
                    print(max(result))
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
    DEEPS = 9
    g = Gomokuy()
    g.parse(a)
    g.mul()
    # print(g.analyse(single_step=False))
    # print(g._ending((7, 3), B))
