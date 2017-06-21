#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from conf import ROADS
B = 1
W = 2


class BaseGame:
    def __init__(self):
        self.over = False
        self.winner = ""
        self.width = 15
        self.table = []
        for i in range(self.width):
            self.table.append([0] * self.width)
        self.records = []
        self.step = 0

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

    def inside_new_cell_loc(self, _row, _col, _direction, _side, _offset):
        new_row = _row + _offset * _side * ROADS[_direction][0]
        new_col = _col + _offset * _side * ROADS[_direction][1]
        if new_row >= self.width or new_row < 0:
            return False
        if new_col >= self.width or new_col < 0:
            return False

        ret_cell = self.table[new_row][new_col]
        ret_loc = (new_row, new_col)
        return ret_loc, ret_cell

    def _ending(self, loc, player):
        def _liner(_direction):
            _counts, _spaces = 1, 0
            for side in (-1, 1):
                for offset in range(1, 9):
                    ret = self.inside_new_cell_loc(loc[0], loc[1], _direction, side, offset)
                    if not ret:
                        break
                    else:
                        (new_x, new_y), new_cell = ret

                    new_cell = self.table[new_x][new_y]
                    if new_cell == player:
                        _counts += 1
                    elif new_cell == 0:
                        _spaces += 1
                        break
                    else:
                        break
            return _counts, _spaces

        for direction in range(4):
            counts, spaces = _liner(direction)
            if counts < 4:
                continue
            elif counts == 4 and spaces == 2:
                self.winner = player
            elif counts == 5:
                self.winner = player
            elif counts > 5:
                self.winner = W
            else:
                continue
            self.over = True
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
        if self.table[loc_x][loc_y] != 0:
            print("这个位置已经有棋了")
            return
        self.step += 1
        player = B if self.step % 2 == 1 else W
        print(f"  go:\t{player}: {loc}")
        self.table[loc_x][loc_y] = player
        self.records.append(list(loc))
        self._ending(loc, player)

    def ungoing(self):
        loc = self.records.pop()
        player = B if self.step % 2 == 1 else W
        print(f"ungo\t{player}: {loc}")
        self.table[loc[0]][loc[1]] = 0
        self.over = False
        self.winner = ""
        self.step -= 1
        return loc

    def retract(self):
        if len(self.records) < 2:
            return
        for loc in [self.records.pop(), self.records.pop()]:
            print(loc)
            self.table[loc[0]][loc[1]] = 0
            self.step -= 2
        self.over = False


