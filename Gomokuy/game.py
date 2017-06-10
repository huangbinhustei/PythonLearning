#!/usr/bin/env python3
# -*- coding: utf-8 -*-

B = 1
W = 2


class Game:
    def __init__(self):
        self.over = False
        self.winner = ""
        self.width = 15
        self.forbidden = False
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

                    new_cell = self.table[new_x][new_y]
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
        if self.table[loc_x][loc_y] != 0:
            print("这个位置已经有棋了")
            return
        self.step += 1
        player = B if self.step % 2 == 1 else W
        # print(f"{player}: {loc}")
        self.table[loc_x][loc_y] = player
        self.records.append(list(loc))
        self._ending(loc, player)

    def retract(self):
        if len(self.records) < 2:
            return
        for loc in [self.records.pop(), self.records.pop()]:
            self.over = False
            print(loc)
            self.table[loc[0]][loc[1]] = 0
