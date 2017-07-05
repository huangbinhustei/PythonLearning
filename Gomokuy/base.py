#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import wraps
import time
import logging
<<<<<<< HEAD

ROADS = {0: (0, 1), 1: (1, 0), 2: (1, 1), 3: (1, -1)}
B = 1
W = 2
PRINTING = {B: "黑", W: "白"}
logger = logging.getLogger('Gomoku')
logger.setLevel(logging.INFO)
=======
import os

logger = logging.getLogger('Gomoku')

def make_logger():

    # 创建一个handler，用于写入日志文件
    file_name = os.path.join("log", time.strftime('%Y-%m-%d', time.localtime(time.time())) + ".txt")
    fh = logging.FileHandler(file_name, encoding="utf-8")
    fh.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # 再创建一个handler，用于输出到控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)


make_logger()
B = 1
W = 2
PRINTING = {B: "黑", W: "白"}
>>>>>>> origin/master


def cost_count(func):
    @wraps(func)
    def costing(*args, **kw):
        a = time.time()
        ret = func(*args, **kw)
        time_cost = int((time.time()-a) * 1000)
<<<<<<< HEAD

        if time_cost > 1000:
            logger.warning("Func(" + str(func.__name__) + ")\tcost: " + str(time_cost) + " ms")
        elif time_cost > 0:
            logger.info("Func(" + str(func.__name__) + ")\tcost: " + str(time_cost) + " ms")
=======
        if time_cost > 0:
            logger.warning("Func(" + str(func.__name__) + ")\tcost: " + str(time_cost) + " ms")
>>>>>>> origin/master
        else:
            time_cost = int((time.time()-a) * 1000000)
            logger.debug("Func(" + str(func.__name__) + ")\tcost: " + str(time_cost) + " μs")
        return ret
    return costing


class BaseGame:
    def __init__(self, restart=False):
        info = "游戏重新开始" if restart else "游戏开始"
        logger.info(info)
        self.winner = ""
        self.width = 15
        self.table = []
        for i in range(self.width):
            self.table.append([0] * self.width)
        self.records = []
        self.step = 0
        self.check = []
        

    def restart(self):
        self.__init__(restart=True)

    def parse(self, manual):
        self.width = len(manual)
        if [len(item) for item in manual] == [self.width] * self.width:
            self.table = manual
            self.step = 0
            for line in manual:
                for cell in line:
                    if cell != 0:
                        self.step += 1
            self.role = W if self.step % 2 else B
            self.other = B if self.role == W else W
        else:
            raise TypeError

<<<<<<< HEAD
    def base_linear(self, row, col, chess, direction):
        def base_effect_loc(_side, _offset):
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
                ret = base_effect_loc(side, offset)
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

    def ending(self, loc, player, show=True):
        self.check = []

        def win(man, info="", show=True):
            self.winner = man
            if show:
                logger.info(f"{self.records}\t{info}")
            else:
                logger.debug(f"{self.records}\t{PRINTING[self.winner]}·{info}")

        four_three_check = [0, 0]
        for direction in range(4):
            line = self.base_linear(loc[0], loc[1], player, direction)
            counts = len(line["s"])
            if line[-1] and line[1]:
                spaces = 2
            elif line[0] or line[1] or line[-1]:
                spaces = 1
            else:
                spaces = 0

            if counts == 5 and not line[0]:
                # counts == 5 但 有line[0] 怎么办？理论上算线的时候就要干掉啊。
                win(player, info=PRINTING[player] + "·五连·胜")
                break
            if counts == 4 and spaces == 2 and not line[0]:
                win(player, info=PRINTING[player] + "·四连·胜")
                break
            if counts > 5 and not line[0]:
                info = "白·长连·胜" if player == W else "黑·长连禁手·负"
                win(W, info=info)
                break
            if counts == 4 and spaces and len(line[0]) <= 1:
                self.check += [line["s"]]
                four_three_check[0] += 1
            if counts == 3 and spaces == 2 and len(line[0]) <= 1:
                self.check += [line["s"]]
                four_three_check[1] += 1
        self.check = sum(self.check, [])
        if four_three_check == [1, 1]:
            win(player, info=PRINTING[player] + "·四三·胜")
            # todo:43不是必胜，堵住4的同时能够形成冲四或者活四，是可以翻盘的
        elif four_three_check[0] >= 2:
            info = "白·四四·胜" if player == W else "黑·四四禁手·负"
            win(W, info=info)
        elif four_three_check[1] >= 2:
            # todo:33不是必胜，只要对方有冲三，就不算。
            info = "白·三三·胜" if player == W else "黑·三三禁手·负"
            win(W, info=info)

    def move(self, loc):
=======
    def win(self, man, info="", show=True):
        self.winner = man
        if show:
            logger.info(f"{self.records}\t{PRINTING[self.winner]} {info} WIN!")
        else:
            logger.debug(f"{self.records}\t{PRINTING[self.winner]} {info} WIN!")

    def going(self, loc):
>>>>>>> origin/master
        if isinstance(loc, str):
            loc = list(map(int, loc.split(",")))
        if self.winner:
            return False
        if max(loc) >= self.width or min(loc) < 0:
<<<<<<< HEAD
            logging.error("子落棋盘外")
            return
        if self.table[loc_x][loc_y] != 0:
            logging.error("这个位置已经有棋了")
            return
        self.step += 1
        player = B if self.step % 2 == 1 else W
        logging.debug(f"  go:\t{player}: {loc}")
        self.table[loc_x][loc_y] = player
=======
            logger.warning("子落棋盘外")
            return False
        row, col = loc
        if self.table[row][col] != 0:
            logger.warning("这个位置已经有棋了")
            return False
        player = W if self.step % 2 else B
        self.table[row][col] = player
>>>>>>> origin/master
        self.records.append(loc)
        self.step += 1
        return player

<<<<<<< HEAD
    def undo(self, counts=1):
        if len(self.records) < counts:
=======
    def undo(self):
        if len(self.records) < 1:
>>>>>>> origin/master
            return
        loc = self.records.pop()
        self.table[loc[0]][loc[1]] = 0
        self.winner = ""
        self.step -= 1
