#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import wraps
import time

ROADS = {0: (0, 1), 1: (1, 0), 2: (1, 1), 3: (1, -1)}
B = 1
W = 2


def cost_count(func):
    @wraps(func)
    def costing(*args, **kw):
        a = time.time()
        ret = func(*args, **kw)
        time_cost = int((time.time()-a) * 1000)
        if time_cost > 0:
            print("Func(" + str(func.__name__) + ")\tcost: " + str(time_cost) + " ms")
        else:
            time_cost = int((time.time()-a) * 1000000)
            print("Func(" + str(func.__name__) + ")\tcost: " + str(time_cost) + " μs")
        return ret
    return costing


class BaseGame:
    def __init__(self):
        self.winner = ""
        self.width = 15
        self.table = []
        for i in range(self.width):
            self.table.append([0] * self.width)
        self.records = []
        self.step = 0
        self.check = []
        self.overdue_chess = []
        self.fresh_lines = {
            B: [],
            W: [],
        }

    def restart(self):
        self.__init__()

    def parse(self, manual):
        self.width = len(manual)
        if [len(item) for item in manual] == [self.width] * self.width:
            self.table = manual
            self.step = 0
            for line in manual:
                for cell in line:
                    if cell != 0:
                        self.step += 1
        else:
            raise TypeError

    def base_linear(self, row, col, chess, direction, radio=False):
        def effect_area(_side, _offset):
            new_row = row + _offset * _side * ROADS[direction][0]
            new_col = col + _offset * _side * ROADS[direction][1]
            if new_row >= self.width or new_row < 0:
                return False
            if new_col >= self.width or new_col < 0:
                return False

            ret_cell = self.table[new_row][new_col]
            ret_loc = (new_row, new_col)
            return ret_loc, ret_cell

        line = {
            "s": [(row, col)],
            0: [],  # 中间的缝隙
            -1: [],  # 某一边的空
            1: [],  # 另一边的空
        }
        for side in (-1, 1):
            for offset in range(1, 9):
                ret = effect_area(side, offset)
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
                            if len(line[side]) <= 2:
                                line[0] = line[side]
                                line[side] = []
                            else:
                                break
                    line["s"].append(new_loc)
                else:
                    if radio:
                        self.overdue_chess.append([new_loc, direction])
                    break
        return line

    def __ending(self, loc, player, show=True):
        def win(man, info=""):
            self.winner = man
            if show:
                print(f"{self.records}\t{self.winner}{info} WIN!")

        def make_fresh_line():
            self.overdue_chess = []
            self.fresh_lines = {
                B: [],
                W: [],
            }

            for direction in range(4):
                line = self.base_linear(loc[0], loc[1], player, direction, radio=True)
                if len(line["s"]) + len(line[-1]) + len(line[0]) + len(line[1]) >= 5:
                    self.fresh_lines[player].append(line)

        def checking_or_ending():
            self.check = []
            four_three_check = [0, 0]
            for line in self.fresh_lines[player]:
                counts = len(line["s"])
                if line[-1] and line[1]:
                    spaces = 2
                elif line[0] or line[1] or line[-1]:
                    spaces = 1
                else:
                    spaces = 0

                if counts == 5 and not line[0]:
                    win(player, info="五子棋胜")
                    break
                if counts == 4 and spaces == 2 and not line[0]:
                    win(player, info="四连胜")
                    break
                if counts > 5 and not line[0]:
                    win(W, info="长连禁手胜")
                    break
                if counts == 4 and spaces and len(line[0]) <= 1:
                    self.check += [line["s"]]
                    four_three_check[0] += 1
                if counts == 3 and spaces == 2 and len(line[0]) <= 1:
                    self.check += [line["s"]]
                    four_three_check[1] += 1
            self.check = sum(self.check, [])
            if four_three_check == [1, 1]:
                win(player, info="四三胜")
            elif max(four_three_check) >= 2:
                win(W, info="禁手胜")

        make_fresh_line()
        checking_or_ending()

    def going(self, loc, show=True):
        if isinstance(loc, str):
            loc = list(map(int, loc.split(",")))
        if self.winner:
            return
        if max(loc) >= self.width or min(loc) < 0:
            print("子落棋盘外")
            return
        row, col = loc
        if self.table[row][col] != 0:
            print("这个位置已经有棋了")
            return
        self.step += 1
        player = B if self.step % 2 == 1 else W
        # print(f"  go:\t{player}: {loc}")
        self.table[row][col] = player
        self.records.append(loc)
        self.__ending(loc, player, show=show)

    def undo(self):
        if len(self.records) < 1:
            return
        loc = self.records.pop()
        self.table[loc[0]][loc[1]] = 0
        self.winner = ""
        self.step -= 1
