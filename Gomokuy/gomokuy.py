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
    def analyse(self, top_n=1):
        status = defaultdict(int)
        self.values = dict()
        self.lines = {
            True: [],
            False: [],
        }
        self.inside_make_line()
        for sid, lines in self.lines.items():
            self.values[sid] = defaultdict(list)
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
            new_score = int(int(str(score*10)[:2])*pow(10, len(str(score))-2))
            temp[new_score].append(loc)
        best_score = max(temp.keys())
        single = choice(temp[best_score])
        mult = (temp[best_score], len(temp[best_score]) * best_score)
        ret = single if top_n == 1 else mult
        return ret

    def _temp(self, me, deeps):
        poss = self.analyse(top_n=2)[0]
        # print(f"deeps:{deeps}\t{len(poss)}")
        result = [0] * len(poss)
        for ind, pos in enumerate(poss):
            self.going(pos)
            if not self.winner:
                if deeps == 0:
                    result[ind] = 0
                else:
                    result[ind] = self._temp(me, deeps - 1)
            elif self.winner == me:
                result[ind] = 1
            else:
                result[ind] = -1
            self.ungoing()

        if deeps == 3:
            # print(f"result is {result}")
            return result
        else:
            return sum(result)/len(result)

    def temp(self, me, deeps):
        if not self.winner:
            if deeps == 0:
                return 0
            else:
                poss = self.analyse(top_n=2)[0]
                result = [0] * len(poss)
                for ind, pos in enumerate(poss):
                    self.going(pos)
                    # print(f"record going:{self.records}")
                    result[ind] = self.temp(me, deeps - 1)
                    self.ungoing()
                    # print(f"record ungoing:{self.records}")
                if deeps == 5:
                    print(poss)
                    return result
                else:
                    return sum(result) / len(result)
        elif self.winner == me:
            return 1
        else:
            return -1

    def ttttt(self):
        me = B if (self.step + 1) % 2 == 1 else W
        print(self.temp(me, 5))


if __name__ == '__main__':
    g = Gomokuy()
    g.parse(a)
    g.ttttt()
