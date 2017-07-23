#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import wraps
import time
import logging

B = 1
W = 2
PRINTING = {B: "黑", W: "白"}
logger = logging.getLogger('Gomoku')


def cost_count(func):
    @wraps(func)
    def costing(*args, **kw):
        a = time.time()
        ret = func(*args, **kw)
        time_cost = time.time()-a

        if time_cost > 1:
            logger.warning("Func(" + str(func.__name__) + ")\tcost: " + str(round(time_cost, 2)) + " s")
        elif time_cost > 0.001:
            time_cost = int(time_cost * 1000)
            logger.info("Func(" + str(func.__name__) + ")\tcost: " + str(time_cost) + " ms")
        else:
            time_cost = int(time_cost * 1000000)
            logger.debug("Func(" + str(func.__name__) + ")\tcost: " + str(time_cost) + " μs")
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

    def move(self, loc, show=True):
        if isinstance(loc, str):
            loc = list(map(int, loc.split(",")))
        if self.winner:
            return
        loc_x, loc_y = loc
        if max(loc) >= self.width or min(loc) < 0:
            logging.error("子落棋盘外")
            return
        if self.table[loc_x][loc_y] != 0:
            logging.error("这个位置已经有棋了")
            return
        self.step += 1
        player = B if self.step % 2 == 1 else W
        logging.debug(f"  go:\t{PRINTING[player]}: {loc}")
        self.table[loc_x][loc_y] = player
        self.records.append(loc)

    def undo(self, counts=1):
        if len(self.records) < counts:
            return
        loc = self.records.pop()
        self.table[loc[0]][loc[1]] = 0
        self.winner = ""
        self.step -= counts
