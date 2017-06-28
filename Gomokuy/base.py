#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from conf import ROADS
B = 1
W = 2


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

    def base_effect_loc(self, _row, _col, _direction, _side, _offset):
        new_row = _row + _offset * _side * ROADS[_direction][0]
        new_col = _col + _offset * _side * ROADS[_direction][1]
        if new_row >= self.width or new_row < 0:
            return False
        if new_col >= self.width or new_col < 0:
            return False

        ret_cell = self.table[new_row][new_col]
        ret_loc = (new_row, new_col)
        return ret_loc, ret_cell

    def base_linear(self, row, col, chess, direction, line):
        for side in (-1, 1):
            for offset in range(1, 9):
                ret = self.base_effect_loc(row, col, direction, side, offset)
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
                    break
        return line

    def ending(self, loc, player):
        self.check = []

        def win(man, info=""):
            self.winner = man
            # print(f"{self.records}\t{self.winner}{info} WIN!")

        four_three_check = [0, 0]
        for direction in range(4):
            line = {
                "s": [(loc[0], loc[1])],
                0: [],  # 中间的缝隙
                -1: [],  # 某一边的空
                1: [],  # 另一边的空
            }
            line = self.base_linear(loc[0], loc[1], player, direction, line)

            counts = len(line["s"])
            if line[-1] and line[1]:
                spaces = 2
            elif line[0] or line[1] or line[-1]:
                spaces = 1
            else:
                spaces = 0

            if counts == 5 and not line[0]:
                # counts == 5 但 有line[0] 怎么办？理论上算线的时候就要干掉啊。
                win(player, info="五子棋胜")
                break
            if counts == 4 and spaces == 2 and not line[0]:
                win(player, info="四连胜")
                break
            if counts > 5 and not line[0]:
                win(W, info="长连禁手胜")
                break
            if counts == 4 and spaces:
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

    def going(self, loc):
        if isinstance(loc, str):
            loc = list(map(int, loc.split(",")))
        if self.winner:
            return
        loc_x, loc_y = loc
        if max(loc) >= self.width or min(loc) < 0:
            print("子落棋盘外")
            return
        if self.table[loc_x][loc_y] != 0:
            print("这个位置已经有棋了")
            return
        self.step += 1
        player = B if self.step % 2 == 1 else W
        # print(f"  go:\t{player}: {loc}")
        self.table[loc_x][loc_y] = player
        self.records.append(loc)
        self.ending(loc, player)

    def fallback(self):
        loc = self.records.pop()
        self.table[loc[0]][loc[1]] = 0
        self.winner = ""
        self.step -= 1

    def retract(self):
        if len(self.records) < 2:
            return
        for loc in [self.records.pop(), self.records.pop()]:
            print(loc)
            self.table[loc[0]][loc[1]] = 0
            self.step -= 2
        self.winner = ""
