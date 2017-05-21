#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from random import choice
from functools import reduce

B = 1
W = 2
ROADS = {
    0: (0, 1),
    1: (1, 0),
    2: (1, 1),
    3: (1, -1),
}
SCORE = {
    # True ：自己，False：对方
    True: {
        "活4": 1000,
        "冲4": 1000,
        "活3": 10,
        "冲3": 10,
    },
    False: {
        "活4": 100,
        "冲4": 100,
        "活3": 1,
    }
}


class Danger:
    def __init__(self, grid, color):
        self.grid = grid
        self.res = dict()
        self.width = len(grid)
        self.color = color
        self.opponent = B if color == W else W

    def __value_calc_single_chessman(self, row, col, color, opponent):
        ret = []
        for direction in range(4):
            liner = [[], [(row, col)], []]
            for side in (-1, 1):
                side_length = len(liner[1 + side]) + len(liner[1])
                if side_length >= 5:
                    continue
                for offset in range(1, 5):
                    new_row = row + offset * side * ROADS[direction][0]
                    new_col = col + offset * side * ROADS[direction][1]
                    if new_row >= self.width or new_row < 0:
                        break
                    if new_col >= self.width or new_col < 0:
                        break

                    new_cell = self.grid[new_row][new_col]
                    new_loc = (new_row, new_col)
                    if new_cell == color:
                        liner[1].append(new_loc)
                    elif new_cell == 0:
                        liner[1 + side].append(new_loc)
                    elif new_cell == opponent:
                        break
            liner[1] = sorted(sorted(liner[1], key=lambda x: x[1]), key=lambda x: x[0])  # 处理liner
            liner[0] = liner[0][:5 - len(liner[1])]
            liner[2] = liner[2][:5 - len(liner[1])]

            if len(liner[0]) + len(liner[1]) + len(liner[2]) >= 5:
                ret.append(liner)
        return ret

    def __calc_single_color(self, color):
        def get_danger_area(l, length, kid):
            if length < 2:
                return []
            if "活" in kid:
                ret = l[0][:1]
                ret += l[2][:1]
            else:
                ret = l[0][:5 - length]
                ret += l[2][:5 - length]
            return ret

        all_lines = []
        self.res[color] = defaultdict(list)
        opponent = B if color == W else W
        for row in range(self.width):
            for col in range(self.width):
                if self.grid[row][col] == color:
                    temp = self.__value_calc_single_chessman(row, col, color, opponent)
                    for line in temp:
                        if line not in all_lines:
                            all_lines.append(line)
        for line in all_lines:
            chang = len(line[1])
            if line[0] and line[2]:
                key = "活" + str(chang)
            elif line[0] or line[1]:
                key = "冲" + str(chang)
            else:
                continue
            area = get_danger_area(line, chang, key)
            if area:
                self.res[color][key].append(area)

    def calc(self):
        for color in (B, W):
            self.__calc_single_color(color)
        return self.choosing()

    def choosing(self):
        status = defaultdict(int)
        for side, sd in self.res.items():
            for kid, loc_groups in sd.items():
                for loc_group in loc_groups:
                    for loc in loc_group:
                        if kid in SCORE[side == self.color]:
                            status[loc[0] * self.width + loc[1]] += SCORE[side == self.color][kid]

        status = sorted(status.items(), key=lambda x: x[1], reverse=True)
        status = [(int(item[0]/self.width), int(item[0] % self.width), item[1]) for item in status]
        if status:
            return status[0][:2]
        else:
            return False

    def __repr__(self):
        return self.res


class Game:
    def __init__(self):
        self.over = False
        self.winner = ""
        self.width = 15
        self.forbidden = False
        self.grid = []
        for i in range(self.width):
            self.grid.append([0] * self.width)
        self.records = []
        self.step = 0

    def restart(self):
        self.__init__()

    def parse(self, manual):
        if [len(item) for item in manual] == [self.width] * self.width:
            self.grid = manual
        else:
            raise TypeError

    def _ending(self, loc, player):
        loc_x, loc_y = loc
        ret = []
        for way_id, way in enumerate(((1, 0), (0, 1), (1, 1), (1, -1))):
            counts, spaces = 1, 0
            for ind, direct in enumerate((-1, 1)):
                block = [True, True]
                for offset in range(1, 5):
                    new_x = loc_x + way[0] * direct * offset
                    new_y = loc_y + way[1] * direct * offset

                    if new_x >= self.width or new_x < 0:
                        break
                    if new_y >= self.width or new_y < 0:
                        break

                    new_cell = self.grid[new_x][new_y]
                    if new_cell == player:
                        counts += 1
                    else:
                        break
            ret.append([counts, spaces, block])
        for counts, spaces, block in ret:
            if counts <= 4:
                continue
            elif counts == 5:
                self.over = True
                self.winner = player
            else:
                self.over = True
                self.winner = W
            print(f"{self.winner} WIN!")

    def going(self, loc):
        if isinstance(loc, str):
            loc = list(map(int, loc.split(",")))
        if self.over:
            return
        loc_x, loc_y = loc
        if max(loc) >= self.width or min(loc) < 0:
            print("子落棋盘外")
            return
        if self.grid[loc_x][loc_y] != 0:
            print("这个位置已经有棋了")
            return
        self.step += 1
        player = B if self.step % 2 == 1 else W
        print(f"{player}: {loc}")
        self.grid[loc_x][loc_y] = player
        self.records.append(list(loc))
        self._ending(loc, player)

    def retract(self):
        if len(self.records) < 2:
            return
        for loc in [self.records.pop(), self.records.pop()]:
            self.over = False
            print(loc)
            self.grid[loc[0]][loc[1]] = 0


class Calc(Game):
    def __init__(self):
        Game.__init__(self)
        self.val = defaultdict(int)

    def __repr__(self):
        def preparing(a):
            a = str(a)
            r = " " * (4 - len(a))
            return r + a

        self.val = defaultdict(int)
        for color in (B, W):
            opponent = B if color == W else W
            for row in range(self.width):
                for col in range(self.width):
                    if self.grid[row][col] == color:
                        self.__value_calc_single_chessman(row, col, color, opponent)

        temp = []
        for i in range(self.width):
            temp.append([0] * self.width)
        for k, v in sorted(self.val.items(), key=lambda x: x[1], reverse=True):
            temp[int(k / self.width)][int(k % self.width)] = v
        ret = ""
        for l1, l2 in zip(self.grid, temp):
            ret += ",".join(map(str, l1)) + "\t: " + ",".join(map(preparing, l2)) + "\n"
        return ret

    def __value_calc_single_chessman(self, row, col, color, opponent):
        ret = []
        for direction in range(4):
            liner = [[], [(row, col)], []]
            for side in (-1, 1):
                side_length = len(liner[1 + side]) + len(liner[1])
                if side_length >= 5:
                    continue
                for offset in range(1, 10):
                    new_row = row + offset * side * ROADS[direction][0]
                    new_col = col + offset * side * ROADS[direction][1]
                    if new_row >= self.width or new_row < 0:
                        break
                    if new_col >= self.width or new_col < 0:
                        break

                    new_cell = self.grid[new_row][new_col]
                    new_loc = (new_row, new_col)
                    if new_cell == color:
                        liner[1].append(new_loc)
                    elif new_cell == 0:
                        liner[1 + side].append(new_loc)
                    elif new_cell == opponent:
                        break
            liner[1] = sorted(sorted(liner[1], key=lambda x: x[1]), key=lambda x: x[0])  # 处理liner
            ret.append(liner)
        return ret

    def __line_to_val(self, t_lines):
        for liner in t_lines:
            if len(liner[0]) + len(liner[1]) + len(liner[2]) < 5:
                continue
            for side in (-1, 1):
                side = 1 + side
                if liner[2 - side]:
                    # 另一边没有被堵住
                    rat = pow(len(liner[1]), 3)
                else:
                    rat = pow(len(liner[1]), 2)
                if len(liner[side]) == 1:
                    rat /= 2
                if len(liner[side]) + len(liner[1]) < 5:
                    rat /= 2
                liner[side] = liner[side][:5 - len(liner[1])]
                for cell in liner[side]:
                    self.val[cell[0] * self.width + cell[1]] += rat

    def calculator(self):
        self.val = defaultdict(int)
        all_line = []
        for color in (B, W):
            opponent = B if color == W else W
            for row in range(self.width):
                for col in range(self.width):
                    if self.grid[row][col] == color:
                        result = self.__value_calc_single_chessman(row, col, color, opponent)
                        if result in all_line:
                            continue
                        all_line += result
        self.__line_to_val(all_line)

        temp = sorted(self.val.items(), key=lambda x: x[1], reverse=True)[0]
        temp = [int(temp[0] / self.width), int(temp[0] % self.width)]
        return temp


def side_func_pvp():
    game = Game()
    while 1:
        pos = input("x,y：")
        game.going(pos)
        print(game.grid)


def side_func_pve():
    game = Calc()
    while not game.over:
        if game.step % 2 == 0:
            pos = input("x,y：")
            if "," in pos:
                game.going(pos)
            else:
                game.retract()
                print(game)
        else:
            game.calculator()
            print(game)


if __name__ == '__main__':
    a = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 2, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    d = Danger(a, B)
    d.calc()
    print(d.res)
