#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from game import Game, B, W
import copy
from random import choice
from functools import reduce

ROADS = {0: (0, 1), 1: (1, 0), 2: (1, 1), 3: (1, -1)}
a = [
    [0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0],   # 0
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 1
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 2
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 3
    [0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0],   # 4
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 5
    [0, 1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0],   # 6
    [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 7
    [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],   # 8
    [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],   # 9
    [0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 10
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]   # 11
#    0  1  2  3  4  5  6  7  8  9  10 11
SCORE = {
    # True ：自己，False：对方
    True: {
        "活4": 100000000,
        "冲4": 100000000,
        "活3": 1000000,
        "冲3": 100000,
        "活2": 9000,
        "冲2": 100,
        "活1": 1,
        "冲1": 1,
    },
    False: {
        "活4": 10000000,
        "冲4": 10000000,
        "活3": 90000,
        "冲3": 10000,
        "活2": 1000,
        "冲2": 10,
        "活1": 1,
        "冲1": 1,
    }
}


class Situation(Game):
    def __init__(self):
        Game.__init__(self)
        self.values = dict()
        self.lines = {
            True: [],
            False: [],
        }

    def inside_make_line(self):
        for row in range(self.width):
            for col in range(self.width):
                chess = self.table[row][col]
                if not chess:
                    continue
                self.inside_make_line_for_single_chessman(row, col, chess)

    def inside_make_line_for_single_chessman(self, row, col, chess):
        def new_cell_loc(_row, _col, _direction, _side, _offset):
            new_row = _row + _offset * _side * ROADS[_direction][0]
            new_col = _col + _offset * _side * ROADS[_direction][1]
            if new_row >= self.width or new_row < 0:
                return False
            if new_col >= self.width or new_col < 0:
                return False

            ret_cell = self.table[new_row][new_col]
            ret_loc = (new_row, new_col)
            return ret_loc, ret_cell

        you = B if chess == W else W
        for direction in range(4):
            line = {
                "s": [(row, col)],
                0: [],  # 中间的缝隙
                -1: [],     # 某一边的空
                1: [],  # 另一边的空
            }
            for side in (-1, 1):
                for offset in range(1, 9):
                    ret = new_cell_loc(row, col, direction, side, offset)
                    if not ret:
                        break
                    else:
                        new_loc, new_cell = ret
                    if new_cell == you:
                        break
                    elif new_cell == 0:
                        line[side].append(new_loc)
                    elif new_cell == chess:
                        if line[side]:
                            if line[0]:
                                break
                            else:
                                if len(line[side]) <= 2:
                                    line[0] = line[side]
                                    line[side] = []
                                else:
                                    break
                        line["s"].append(new_loc)
            self.inside_line_merge(line, chess)

    def inside_line_merge(self, line, chess):
        line["s"] = sorted(sorted(line["s"], key=lambda x: x[1]), key=lambda x: x[0])  # 处理liner
        line[-1] = line[-1][:5 - len(line["s"])]
        line[1] = line[1][:5 - len(line["s"])]
        me = B if (self.step + 1) % 2 == 1 else W
        if len(line["s"]) + len(line[-1]) + len(line[0]) + len(line[1]) < 5:
            return
        if line not in self.lines[chess == me]:
            self.lines[chess == me].append(line)

    def inside_analyse(self):
        self.values = dict()
        self.lines = {
            True: [],
            False: [],
        }
        self.inside_make_line()
        for sid, lines in self.lines.items():
            self.values[sid] = defaultdict(list)
            for line in lines:
                chang = len(line["s"])
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
                for k in (-1, 0, 1):
                    if line[k]:
                        self.values[sid][key].append(line[k])

    def choosing(self, top_n=1):
        self.inside_analyse()
        status = defaultdict(int)
        for side, sd in self.values.items():
            for kid, loc_groups in sd.items():
                for loc_group in loc_groups:
                    for loc in loc_group:
                        if kid in SCORE[side]:
                            status[loc] += SCORE[side][kid]
        status = sorted(status.items(), key=lambda x: x[1], reverse=True)
        status = [item[0] for item in status]
        ret = status[0] if top_n == 1 else status[:top_n]
        return ret


if __name__ == '__main__':
    g = Situation()
    g.parse(a)
    g.choosing(top_n=3)
