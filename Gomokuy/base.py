#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import wraps
import time
import logging

logger = logging.getLogger('Gomoku')
logger.setLevel(logging.DEBUG)

# 创建一个handler，用于写入日志文件
file_name = time.strftime('%Y-%m-%d', time.localtime(time.time())) + ".log"
fh = logging.FileHandler(file_name, encoding="utf-8")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

# 再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
ch.setFormatter(formatter)
logger.addHandler(ch)


B = 1
W = 2
PRINTING = {B: "黑", W: "白"}


def cost_count(func):
    @wraps(func)
    def costing(*args, **kw):
        a = time.time()
        ret = func(*args, **kw)
        time_cost = int((time.time()-a) * 1000)
        if time_cost > 0:
            logger.warning("Func(" + str(func.__name__) + ")\tcost: " + str(time_cost) + " ms")
        else:
            time_cost = int((time.time()-a) * 1000000)
            logger.debug("Func(" + str(func.__name__) + ")\tcost: " + str(time_cost) + " μs")
        return ret
    return costing


class BaseGame:
    def __init__(self, role=W, restart=False):
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
        self.role = role
        self.other = B if role == W else W

    def restart(self, role=W):
        self.__init__(role=role, restart=True)
        if role == B:
            self.going((7, 7))

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

    def win(self, man, info="", show=True):
        self.winner = man
        if show:
            logger.info(f"{self.records}\t{PRINTING[self.winner]} {info} WIN!")
        else:
            logger.debug(f"{self.records}\t{PRINTING[self.winner]} {info} WIN!")

    def going(self, loc):
        if isinstance(loc, str):
            loc = list(map(int, loc.split(",")))
        if self.winner:
            return False
        if max(loc) >= self.width or min(loc) < 0:
            logger.warning("子落棋盘外")
            return False
        row, col = loc
        if self.table[row][col] != 0:
            logger.warning("这个位置已经有棋了")
            return False
        player = W if self.step % 2 else B
        self.table[row][col] = player
        self.records.append(loc)
        self.step += 1
        return player

    def undo(self):
        if len(self.records) < 1:
            return
        loc = self.records.pop()
        self.table[loc[0]][loc[1]] = 0
        self.winner = ""
        self.step -= 1
