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
                    ret = self.inside_make_line_for_single_chessman(row, col, chess, direction, line)
                    checked |= ret

    def inside_make_line_for_single_chessman(self, row, col, chess, direction, line):
        for side in (-1, 1):
            for offset in range(1, 9):
                ret = self.inside_new_cell_loc(row, col, direction, side, offset)
                if not ret:
                    break
                else:
                    new_loc, new_cell = ret

                if new_cell == 0:
                    line[side].append(new_loc)
                elif new_cell == chess:
                    if line[side]:
                        if line[0]:
                            break
                        else:
                            if len(line[side]) < 2:
                                line[0] = line[side]
                                line[side] = []
                            else:
                                break
                    line["s"].append(new_loc)
                else:
                    break
        self.inside_line_merge(line, chess)
        return set(line["s"])

    def inside_line_merge(self, line, chess):
        line[-1] = line[-1][:5 - len(line["s"])]
        line[1] = line[1][:5 - len(line["s"])]
        me = B if (self.step + 1) % 2 == 1 else W
        if len(line["s"]) + len(line[-1]) + len(line[0]) + len(line[1]) < 5:
            return
        self.lines[chess == me].append(line)

    # @cost_count
    def analyse(self, single_step=True):
        self.values = dict()
        self.lines = {
            True: [],
            False: [],
        }
        self.inside_make_line()
        for sid, lines in self.lines.items():
            status = defaultdict(int)
            for line in lines:
                chang = 5 - len(line[0]) if len(line["s"]) + len(line[0]) > 5 else len(line["s"])
                if line[-1] and line[1]:
                    key = "活" + str(chang)
                    line[-1] = line[-1][:1]
                    line[1] = line[1][:1]
                elif line[0] or line[1] or line[-1]:
                    key = "冲" + str(chang)
                    line[-1] = line[-1][:5 - chang]
                    line[1] = line[1][:5 - chang]
                else:
                    continue

                base_score = SCORE[sid][key] if key in SCORE[sid] else 0
                for k in (-1, 0, 1):
                    for loc in line[k]:
                        status[loc] += base_score
            temp = defaultdict(list)
            for loc, score in status.items():
                new_score = int(int(str(score * 10)[:2]) * pow(10, len(str(score)) - 2))
                temp[new_score].append(loc)
            self.values[sid] = temp

        if max(self.values[True].keys()) >= max(self.values[False].keys()):
            # 如果己方数字更大，那么优先进攻

            m = max(self.values[False].keys())
            key_group = [k for k in self.values[True].keys() if k >= m]
            # 进攻范围是只要攻击力大于对方的就行

            best_pos_group = [self.values[True][k] for k in key_group]
            best_pos_group = sum(best_pos_group, [])
        else:
            # 防守
            best_score = max(self.values[False].keys())
            best_pos_group = self.values[False][best_score]

        single = choice(best_pos_group)
        mul = best_pos_group
        ret = single if single_step == 1 else mul
        return ret

    def temp(self, me, deeps):
        def logging(_pos, _deeps):
            if _deeps == DEEPS:
                print(f"\nThe first step is {_pos}")

        if not self.winner:
            if deeps == 0:
                return 0
            else:
                poss = self.analyse(single_step=False)
                result = [0] * len(poss)
                for ind, pos in enumerate(poss):
                    logging(pos, deeps)
                    self.going(pos)
                    result[ind] = self.temp(me, deeps - 1)
                    self.ungoing()
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

    def mul(self):
        me = B if (self.step + 1) % 2 == 1 else W
        print(self.temp(me, DEEPS))


if __name__ == '__main__':
    DEEPS = 6
    g = Gomokuy()
    g.parse(a)
    g.mul()
    # print(g.analyse(single_step=False))
