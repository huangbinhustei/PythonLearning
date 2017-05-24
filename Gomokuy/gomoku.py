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
a = [
    [0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
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


def show_line(l):
    pr = ""
    for box in l:
        nb = ",".join(["-".join(map(str, cell)) for cell in box])
        nb += " " * (20 - len(nb))
        pr += nb
        pr += "| "
    print(pr[:-2])


class Situation:
    def __init__(self, grid, me):
        self.grid = grid
        self.width = len(grid)
        self.lines = {
            True: [],
            False: [],
        }
        self.me = me
        self.values = dict()
        '''
        values = {
            己方（true)：{
                    活4：[[左空格],[连续棋子],[右空格]]，
                    冲4: [[左空格],[连续棋子],[右空格]]，
                },
            对方：
                
        }
        '''

    def __single_chessman(self, row, col, chess):
        you = B if chess == W else W
        for direction in range(4):
            line = [[], [(row, col)], []]
            for side in (-1, 1):
                jump = False
                for offset in range(1, 5):
                    new_row = row + offset * side * ROADS[direction][0]
                    new_col = col + offset * side * ROADS[direction][1]
                    if new_row >= self.width or new_row < 0:
                        break
                    if new_col >= self.width or new_col < 0:
                        break

                    new_cell = self.grid[new_row][new_col]
                    new_loc = (new_row, new_col)
                    if new_cell == chess:
                        if jump:
                            line[1 + side].append(new_loc)
                        else:
                            line[1].append(new_loc)
                    elif new_cell == 0:
                        side_length = len(line[1 + side]) + len(line[1])
                        if side_length < 5:
                            jump = True
                            line[1 + side].append(new_loc)
                    elif new_cell == you:
                        break
            line[1] = sorted(sorted(line[1], key=lambda x: x[1]), key=lambda x: x[0])  # 处理liner
            line[0] = line[0][:5 - len(line[1])]
            line[2] = line[2][:5 - len(line[1])]
            if len(sum(line, [])) < 5:
                continue
            if line in self.lines[chess == self.me]:
                continue
            self.lines[chess == self.me].append(line)

    def make_line(self):
        for row in range(self.width):
            for col in range(self.width):
                chess = self.grid[row][col]
                if not chess:
                    continue
                self.__single_chessman(row, col, chess)
        for sid, lines in self.lines.items():
            print(sid)
            list(map(show_line, lines))

    def line2value(self):
        for sid, lines in self.lines.items():
            self.values[sid] = defaultdict(list)
            for line in lines:
                chang = len(line[1])
                if line[0] and line[2]:
                    key = "活" + str(chang)
                    line[0] = line[0][:1]
                    line[2] = line[2][:1]
                elif line[0] or line[1]:
                    key = "冲" + str(chang)
                    line[0] = line[0][:5 - chang]
                    line[2] = line[2][:5 - chang]
                else:
                    continue
                if line[0]:
                    self.values[sid][key].append(line[0])
                if line[2]:
                    self.values[sid][key].append(line[2])
        print(self.values)

    def choosing(self):
        self.make_line()
        self.line2value()
        status = defaultdict(int)
        for side, sd in self.values.items():
            for kid, loc_groups in sd.items():
                for loc_group in loc_groups:
                    for loc in loc_group:
                        if kid in SCORE[side]:
                            status[loc[0] * self.width + loc[1]] += SCORE[side][kid]

        status = sorted(status.items(), key=lambda x: x[1], reverse=True)
        status = [(int(item[0] / self.width), int(item[0] % self.width), item[1]) for item in status]
        if status:
            return status[0][:2]
        else:
            return False


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

if __name__ == '__main__':
    s = Situation(a, W)
    s.make_line()
    s.line2value()
    print(s.choosing())
