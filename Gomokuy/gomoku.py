#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict

B = 1
W = 2
ROADS = {
    0: (0, 1),
    1: (1, 0),
    2: (1, 1),
    3: (1, -1),
}


class Game:
    def __init__(self):
        self.over = False
        self.winner = ""
        self.width = 12
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
                    elif new_cell == 0:
                        spaces += 1
                        block[ind] = False
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
        self.records.append(loc)
        self._ending(loc, player)

    def retract(self):
        if len(self.records) <= 2:
            return
        for loc in [self.records.pop(), self.records.pop()]:
            print(loc)
            self.grid[loc[0]][loc[1]] = 0


class Calc(Game):
    def __init__(self):
        Game.__init__(self)
        self.val = defaultdict(int)

    def __repr__(self):
        def preparing(a):
            a = str(a)
            r = " "*(4-len(a))
            return r + a

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
        for direction in range(4):
            liner = [False, [], [], [], False]
            # False表示没有堵住
            for side in [-1, 1]:
                for offset in range(1, 5):
                    new_row = row + offset * side * ROADS[direction][0]
                    new_col = col + offset * side * ROADS[direction][1]
                    if new_row >= self.width or new_row < 0:
                        liner[2 + 2 * side] = True
                        # 墙表示堵住
                        break
                    if new_col >= self.width or new_col < 0:
                        liner[2 + 2 * side] = True
                        # 墙表示堵住
                        break

                    new_cell = self.grid[new_row][new_col]
                    new_loc = [[new_row, new_col], pow(2, offset-1)]
                    if new_cell == color:
                        liner[2].append(new_loc)
                    elif new_cell == 0:
                        liner[2 + side].append(new_loc)
                    elif new_cell == opponent:
                        liner[2 + 2 * side] = True
                        # 对方的子表示堵住
                        break
            if len(liner[1]) + len(liner[2]) + len(liner[3]) < 5:
                continue
            for side in (-1, 1):
                side = 2 + side
                rate = 32
                if len(liner[side]) + len(liner[2]) < 5:
                    rate = int(rate / 2)

                rate = int(rate / 2) if (liner[0] or liner[-1]) else rate
                for cell in liner[side]:
                    self.val[cell[0][0] * self.width + cell[0][1]] += int(rate / cell[1]) * len(liner[2]) * len(liner[2])

    def calculator(self):
        self.val = defaultdict(int)
        for color in (B, W):
            opponent = B if color == W else W
            for row in range(self.width):
                for col in range(self.width):
                    if self.grid[row][col] == color:
                        self.__value_calc_single_chessman(row, col, color, opponent)
        temp = sorted(self.val.items(), key=lambda x: x[1], reverse=True)[0]
        temp = [int(temp[0] / self.width), int(temp[0] % self.width)]
        if self.grid[temp[0]][temp[1]] != 0:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(temp)
        self.going(temp)


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
    side_func_pve()
