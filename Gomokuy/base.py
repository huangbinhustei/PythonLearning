#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import wraps
import time
import logging
from collections import defaultdict
import random


B = 1
W = 2
PRINTING = {B: "黑", W: "白"}
cost_dict = defaultdict(lambda: [0, 0.0])
ROADS = {0: (0, 1), 1: (1, 0), 2: (1, 1), 3: (1, -1)}
ADR = {
    0: {
        "冲1": 0, "冲2": 2, "冲3": 2, "冲4": 1, "冲5": 0, "冲6": 0,
        "活1": 1, "活2": 1, "活3": 1, "活4": 1, "活5": 0, "活6": 0},
    1: {
        "冲1": 0, "冲2": 2, "冲3": 1, "冲4": 0, "冲5": 0, "冲6": 0,
        "活1": 1, "活2": 1, "活3": 1, "活4": 0, "活5": 0, "活6": 0},
    2: {
        "冲1": 0, "冲2": 1, "冲3": 0, "冲4": 0, "冲5": 0, "冲6": 0,
        "活1": 1, "活2": 1, "活3": 0, "活4": 0, "活5": 0, "活6": 0},
}
info = ""
logger = logging.getLogger('Gomoku')
logger.addHandler(logging.StreamHandler())


def timing(func):
    @wraps(func)
    def costing(*args, **kw):
        a = time.time()
        ret = func(*args, **kw)
        time_cost = time.time() - a
        global cost_dict
        cost_dict[func.__name__][0] += 1
        cost_dict[func.__name__][1] += time_cost
        return ret
    return costing


class BaseGame:
    def __init__(self, restricted=True):
        self.winner = False
        self.width = 15
        self.table = []
        for i in range(self.width):
            self.table.append([0] * self.width)
        self.records = []
        self.step = 0
        self.restricted = restricted
        self.values = {
            B: defaultdict(list),
            W: defaultdict(list)}
        self.check = []

        self.zod_grid = []
        self.zod_key = 0
        ra = 2 ** 105
        for i in range(self.width):
            t = []
            for j in range(self.width):
                t1 = []
                for k in range(3):
                    t1.append(int(random.random() * ra))
                t.append(t1)
            self.zod_grid.append(t)
        self.translation_table = dict()

    def get_zod(self, deep):
        k = self.zod_key
        if k in self.translation_table:
            if self.translation_table[k]["result"] == 9999999 or deep <= self.translation_table[k]["deep"]:
                return [self.translation_table[k]["pos"]]
        else:
            return False

    def restart(self):
        self.__init__()

    def parse(self, manual):
        self.width = len(manual)
        if [len(item) for item in manual] == [self.width] * self.width:
            self.table = manual
            self.step = 0
            for row, line in enumerate(manual):
                for col, cell in enumerate(line):
                    self.zod_key ^= self.zod_grid[row][col][cell]
                    if cell != 0:
                        self.step += 1
        else:
            raise TypeError

    @timing
    def modify_values(self, loc, chess):
        row, col = loc
        for direction in range(4):
            line = self.base_linear(row, col, chess, direction)
            self.values = self.inside_line_grouping(line, chess, self.values)

    @timing
    def base_linear(self, row, col, chess, direction):
        line = {
            "s": [(row, col)],
            0: [],  # 中间的缝隙
            -1: [],  # 某一边的空
            1: []}  # 另一边的空
        for side in (-1, 1):
            for offset in range(1, 6):
                new_row = row + offset * side * ROADS[direction][0]
                new_col = col + offset * side * ROADS[direction][1]
                if new_row >= self.width or new_row < 0:
                    break
                if new_col >= self.width or new_col < 0:
                    break

                new_cell = self.table[new_row][new_col]
                new_loc = (new_row, new_col)

                if new_cell == 0:
                    line[side].append(new_loc)
                elif new_cell == chess:
                    if line[side]:
                        if line[0]:
                            break
                        else:
                            if len(line[side]) <= 1:
                                line[0] = line[side]
                                line[side] = []
                            else:
                                break
                    line["s"].append(new_loc)
                else:
                    break
        return line

    @timing
    def inside_make_line(self, side=False):
        self.values = {
            B: defaultdict(list),
            W: defaultdict(list)}

        for direction in range(4):
            checked = set([])
            for row, t_line in enumerate(self.table):
                for col, chess in enumerate(t_line):
                    if not chess:
                        continue
                    if (row, col) in checked:
                        continue
                    if side and chess != side:
                        continue
                    line = self.base_linear(row, col, chess, direction)
                    checked |= set(line["s"])
                    if len(line["s"]) + len(line[-1]) + len(line[0]) + len(line[1]) < 5:
                        continue
                    self.values = self.inside_line_grouping(line, chess, self.values)

    @timing
    def inside_line_grouping(self, line, chess, values):
        t = len(line["s"])
        t = 6 if t >= 6 else t
        if line[-1] and line[1]:
            key = "活" + str(t) if t + len(line[0]) <= 4 else "冲" + str(t)
        elif line[0] or line[1] or line[-1]:
            key = "冲" + str(t)
        else:
            return values
        sli = ADR[len(line[0])][key]
        line[-1] = line[-1][:sli]
        line[1] = line[1][:sli]
        format_line = line[-1] + line[0] + line[1]
        values[chess][key].append(format_line)
        return values

    @timing
    def judge(self, loc, player, show=True):
        row, col = loc
        _opt = B if player == W else W
        self.check = []

        # @timing
        def judge_first():
            global info
            four_three = [0, 0]

            for direction in range(4):
                line = self.base_linear(row, col, player, direction)
                chang = len(line["s"])

                if chang > 5 and not line[0]:
                    self.check += line["s"]
                    if self.restricted:
                        self.winner = W
                        info = "白·长连·胜!" if player == W else "黑·长连禁手·负!"
                    else:
                        self.winner = player
                        info = PRINTING[player] + "·长连·胜!"
                    return True
                elif chang == 5 and not line[0]:
                    self.winner = player
                    info = PRINTING[player] + "·五连·胜!"
                    self.check += line["s"]
                    return True
                elif chang == 4:
                    self.check += line["s"]
                    if line[0]:
                        four_three[0] += 1
                        block = line[0][0]
                    elif line[-1] and line[1]:
                        self.winner = player
                        info = PRINTING[player] + "·四连·胜!"
                        return True
                    elif line[-1] or line[1]:
                        four_three[0] += 1
                        temp = line[-1] or line[1]
                        block = temp[0]
                elif chang == 3 and line[1] and line[-1]:
                    four_three[1] += 1
                    self.check += line["s"]

            if four_three[0] >= 2:
                if self.restricted:
                    self.winner = W
                    info = "白·四四·胜!" if player == W else "黑·四四禁手·负!"
                else:
                    self.winner = player
                    info = PRINTING[player] + "·四四·胜!"
                return True
            elif four_three[1] >= 2:
                if player == B and self.restricted:
                    self.winner = W
                    info = "黑·三三禁手·负!"
                    return True
                else:
                    # 有可能三三胜
                    return False
            elif sum(four_three) >= 2:
                row_o, col_o = block
                for direction in range(4):
                    line = self.base_linear(row_o, col_o, _opt, direction)
                    if len(line["s"]) >= 4:
                        break
                else:
                    self.winner = player
                    info = PRINTING[player] + "·四三·胜!"
                    return True
            return True

        # @timing
        def judge_second():
            # 双活三，需要看对方是否有冲三、冲四、活三
            # 禁手已经处理掉了，这里只管赢
            values = {
                B: defaultdict(list),
                W: defaultdict(list)}

            for direction in range(4):
                checked = set([])
                for row, t_line in enumerate(self.table):
                    for col, chess in enumerate(t_line):
                        if chess != _opt:
                            continue
                        if (row, col) in checked:
                            continue
                        line = self.base_linear(row, col, chess, direction)
                        checked |= set(line["s"])
                        if len(line["s"]) < 3:
                            continue
                        if len(line["s"]) + len(line[-1]) + len(line[0]) + len(line[1]) < 5:
                            continue
                        values = self.inside_line_grouping(line, _opt, values)

            if values[_opt]["活3"] or values[_opt]["冲3"] or values[_opt]["冲4"]:
                pass
            else:
                self.winner = player
                global info
                info = PRINTING[player] + "·三三·胜"

        judge_first() or judge_second()

        if not self.winner:
            return
        if show:
            logger.info(f"{info}\t{self.records}")
        else:
            logger.debug(f"{info}\t{self.records}")

    @timing
    def move(self, loc, show=True):
        if isinstance(loc, str):
            loc = list(map(int, loc.split(",")))
        if self.winner:
            return False
        if max(loc) >= self.width or min(loc) < 0:
            logger.error("子落棋盘外")
            return False
        row, col = loc
        if self.table[row][col] != 0:
            logger.error("这个位置已经有棋了")
            return False
        self.step += 1
        player = B if self.step % 2 == 1 else W
        self.table[row][col] = player
        self.zod_key ^= self.zod_grid[row][col][0] ^ self.zod_grid[row][col][player]
        self.records.append(loc)
        self.judge(loc, player, show=show)
        # self.modify_values(loc, player)

    def undo(self, count=1):
        if len(self.records) < count:
            logger.error("悔棋失败！！！！！")
            return
        for i in range(count):
            row, col = self.records.pop()
            tmp = self.table[row][col]
            self.table[row][col] = 0
            self.zod_key ^= self.zod_grid[row][col][tmp] ^ self.zod_grid[row][col][0]
        self.winner = False
        self.step -= count
