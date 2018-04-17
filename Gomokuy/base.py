#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import wraps
import time
import logging
from collections import defaultdict
import numpy as np
import random

from conf import a, LC

B = 0
W = 1
PRINTING = {B: "黑", W: "白"}
cost_dict = defaultdict(lambda: [0, 0.0])
ROADS = {0: (0, 1), 1: (1, 0), 2: (1, 1), 3: (1, -1)}
info = ""
logger = logging.getLogger('Gomoku')
logger.addHandler(logging.StreamHandler())


def timing(func):
    @wraps(func)
    def costing(*args, **kw):
        time_start = time.time()
        ret = func(*args, **kw)
        time_cost = time.time() - time_start
        cost_dict[func.__name__][0] += 1
        cost_dict[func.__name__][1] += time_cost
        return ret
    return costing


def init_ways():
    ret = []
    for row in range(15):
        for col in range(15):
            line = []
            for direction in range(4):
                tmp_line = [(row, col)]
                for side in (-1, 1):
                    for offset in range(1, 10):
                        new_row = row + offset * side * ROADS[direction][0]
                        new_col = col + offset * side * ROADS[direction][1]
                        if new_row >= 15 or new_row < 0:
                            break
                        if new_col >= 15 or new_col < 0:
                            break
                        new_loc = (new_row, new_col)
                        if side == 1:
                            tmp_line.append(new_loc)
                        else:
                            tmp_line.insert(0, new_loc)
                line.append(tmp_line)
            ret.append(line)
    return ret


def show_timing():
    print("\nTiming\n+-%-24s-+-%-12s-+-%-8s-+" % ("-" * 24, "-" * 12, "-" * 8))
    print("| %-24s | %-12s | %-8s |" % ("Func name", "Times", "Cost(ms)"))
    print("+-%-24s-+-%-12s-+-%-8s-+" % ("-" * 24, "-" * 12, "-" * 8))
    for k, v in cost_dict.items():
        print("| %-24s | %-12d | %-8s |" % (k, v[0], str(int(v[1] * 1000))))
    print("+-%-24s-+-%-12s-+-%-8s-+\n" % ("-" * 24, "-" * 12, "-" * 8))


@timing
def four_to_one(tmp):
    # ret = c_int(0)
    # input = (c_int * 4)()
    # for i in range(0, len(input)):
    #     input[i] = tmp[i]
    # ret = libc.four_to_one(input)
    # print(ret)
    # print(max(tmp))

    return max(tmp)


class BlackWhite:
    def __init__(self, forbidden=True):
        self.step = 0
        self.records = []
        self.winner = 2
        self.forbidden = forbidden
        self.dangerous = []  # 将军的棋子
        self.forced = False # 自己这一步是否是被迫走的

        self.table = np.array([[2] * 225]).reshape(15, 15)
        self.score = np.array([[0] * 450]).reshape(15, 15, 2)
        self.sub_score = np.array([[0] * 1800]).reshape(15, 15, 8)

        self.candidates = []
        self.situation = 0

        self.zob_grid = []
        self.zob_key = 0
        ra = 2 ** 105
        for i in range(15):
            t = []
            for j in range(15):
                t1 = []
                for k in range(3):
                    t1.append(int(random.random() * ra))
                t.append(t1)
            self.zob_grid.append(t)
        self.translation_table = dict()

        self.ways = init_ways()

    def _winning(self, sid, line=False, show=True, attack=[]):
        def declaring(p, information):
            self.winner = p
            if show:
                logger.info(f"{PRINTING[sid]}方{information}")
            else:
                logger.debug(f"{PRINTING[sid]}{information}")

        def _win_by_line():
            if sid == W:
                declaring(W, "五连胜")
            else:
                # 黑方需要判断是否有禁手
                left = [line[0][0] * 2 - line[1][0], line[0][1] * 2 - line[1][1]]
                right = [line[-1][0] * 2 - line[-2][0], line[-1][1] * 2 - line[-2][1]]
                if self.table[left[0]][left[1]] == B or self.table[right[0]][right[1]] == B:
                    declaring(W, "长连禁手负！")
                else:
                    declaring(B, "五连胜")

        def _win_by_attack():
            opt = W if sid == B else B

            chance_of_your = self.score[:, :, opt]
            best_score_your = np.max(chance_of_your)

            if 6 in attack:
                # 构成活四
                if best_score_your < 9:
                    # 只要对方当前没有冲四，就获胜
                    declaring(sid, "四连胜")
            elif attack.count(5) >= 2:
                if sid == B:
                    declaring(W, "禁手胜")
                else:
                    declaring(W, "获胜")
            elif attack.count(4) >= 2:
                if sid == B:
                    declaring(W, "禁手胜")
                elif best_score_your < 5:
                    # 三三时只要对方有冲四就不能算赢
                    declaring(W, "获胜")

            elif 5 in attack and 4 in attack:
                chance_of_mine = self.score[:, :, sid]
                danger_pos = list(zip(*np.where(chance_of_mine == np.max(chance_of_mine))))
                for pos in danger_pos:
                    if pos == self.records[-1]:
                        continue
                    if chance_of_your[pos[0]][pos[1]] >= 5:
                        # 假如对方堵住冲四的时候能够构成冲四，那么就不算赢。
                        break
                else:
                    # 胜利
                    declaring(sid, "四三胜")

        if line:
            _win_by_line()
        elif attack:
            _win_by_attack()

    def get_way(self, row, col):
        return self.ways[row * 15 + col]

    @timing
    def _aoe_when_move_or_undo(self, row, col, show=True):
        def zobing():
            zob = self.get_zob()
            if not zob:
                # 新情况，等待存入数据
                return False
            self.candidates = zob["candidates"].copy()
            self.score = zob["score"].copy()
            self.sub_score = zob["sub_score"].copy()
            self.forced = zob["forced"]
            return True

        # 不管是下棋还是悔棋，这些都是受影响的区域，需要重新计算结果
        def get_offset_by_block(fir, sec, sd):
            def siding(side_location):
                # 用于判断边上是否堵住了，仅用于 line_ordering 函数
                # 返回 True 表示没有堵住
                if min(side_location) < 0 or max(side_location) >= 15:
                    return False
                else:
                    return False if self.table[side_location[0]][side_location[1]] == opt else True

            opt = B if sd == W else W
            bool_left = siding(fir)
            bool_right = siding(sec)
            if bool_left:
                block = 0 if bool_right else 2
            else:
                block = 1 if bool_right else 3
            return block
        
        @timing
        def line_ordering(line):
            def get_ind():
                rate = 1
                ind = 0
                for item in chesses[::-1]:
                    if item != 2:
                        ind += rate
                    rate *= 2
                return ind

            # 将连续五颗字整型，仅用于 self.aoe 函数
            chesses = [self.table[item[0]][item[1]] for item in line]

            if W in chesses and B in chesses:
                return False

            left = [line[0][0] * 2 - line[1][0], line[0][1] * 2 - line[1][1]]
            right = [line[-1][0] * 2 - line[-2][0], line[-1][1] * 2 - line[-2][1]]

            if B in chesses:
                situation = get_ind()
                if situation == 31:
                    # 5连了
                    self._winning(B, line=line, show=show)
                n_block = get_offset_by_block(left, right, B)
                return [B, line, chesses, situation, LC[situation][n_block]]
            elif W in chesses:
                situation = get_ind()
                if situation == 31:
                    self._winning(W, line=line, show=show)
                n_block = get_offset_by_block(left, right, W)
                return [W, line, chesses, situation, LC[situation][n_block]]
            else:
                return False

        @timing
        def line_filter(line_input):
            def t(l):
                # print(line_input)
                # print(l)
                ret=[]
                flag = l[0]
                tmp = [flag]
                for x in l[1:]:
                    if x == flag:
                        tmp.append(x)
                    else:
                        ret.append(tmp)
                        tmp = [x]
                        flag = x
                ret.append(tmp)

                fin = set([0])
                offset = 0
                for ind, line in enumerate(ret):
                    lg = len(line)
                    if line[0] == 2:
                        offset += lg
                        continue
                    if ind > 0 and ret[ind-1][0] == 2:
                        start = offset - 5 + lg
                        if start >= 0:
                            fin.add(start)
                    if ind < len(ret)-1 and ret[ind+1][0] == 2:
                        fin.add(offset)
                    if lg >= 5:
                        fin.add(offset)
                    offset += lg
                fin = [line_input[i: i + 5] for i in fin]
                # fin.append(line_input[start: start + 5])
                return fin
            inp = [self.table[row][col] for row, col in line_input]

            line_output = []
            # print(f"{t(inp)}")
            return t(inp)
            # for i in t(inp):
                # line_output.append(i)
            # print(f"!!!!!!!\nline_input\t{line_input}")
            # return line_output

        if zobing():
            return

        ret = []
        changes = dict()
        self.sub_score[row][col] = [0, 0, 0, 0, 0, 0, 0, 0]

        aoe_line = self.get_way(row, col)
        for direction in range(4):
            tmp_line = aoe_line[direction]
            for new_row, new_col in tmp_line:
                self.sub_score[new_row][new_col][direction] = 0
                self.sub_score[new_row][new_col][direction + 4] = 0

            for l in line_filter(tmp_line):
                if len(l) == 5:
                    ordered_line = line_ordering(l)
                    if ordered_line:
                        ret.append([direction, ordered_line])

        for l in ret:
            direction, [sid, locations, _, _, result] = l
            for ind, loc in enumerate(locations):
                key = (sid, direction, loc)
                if key in changes:
                    changes[key] = max(int(result[ind]), changes[key])
                else:
                    changes[key] = int(result[ind])
        for k, v in changes.items():
            sid, direction, (row, col) = k
            offset = sid * 4 + direction
            self.sub_score[row][col][offset] = v

        for direction in range(4):
            tmp_line = aoe_line[direction]
            for row, col in tmp_line:
                values = self.sub_score[row][col]
                self.score[row][col] = [four_to_one(values[0: 4]), four_to_one(values[4: 8])]

        self._gen()
        self.set_zob()

    @timing
    def _gen(self):
        def _king_finding():
            fir = list(zip(*np.where(chance_of_mine[:, :] >= 8)))
            if fir:
                return fir
            else:
                sec = list(zip(*np.where(chance_of_your[:, :] >= 8)))
                if sec:
                    # 返回的 True 表示自己这一步是不得不走
                    self.forced = True
                    return sec
                else:
                    return list(zip(*np.where(chance_of_mine[:, :] >= 6)))

        def _queen_finding():
            return list(zip(*np.where(chance_of_mine[:, :] >= 4))) + list(zip(*np.where(chance_of_your[:, :] >= 5)))

        def _knight_finding():
            return list(zip(*np.where(chance_of_mine[:, :] >= 2))) + list(zip(*np.where(chance_of_your[:, :] >= 4)))

        def _soldier_finding():
            return list(zip(*np.where(chance_of_mine[:, :] >= 1))) + list(zip(*np.where(chance_of_your[:, :] >= 1)))

        self.forced = False
        next_player = B if self.step % 2 == 0 else W
        opt_player = B if next_player == W else W
        chance_of_mine = self.score[:, :, next_player]
        chance_of_your = self.score[:, :, opt_player]

        self.candidates = _king_finding() or _queen_finding()
        if not self.candidates:
            knight = _knight_finding()
            if knight:
                self.candidates = knight[:5]
            else:
                self.candidates = _soldier_finding()

        self.situation = np.sum(chance_of_mine) - np.sum(chance_of_your)

    def load(self, table, records=False):
        if not records:
            blacks = []
            whites = []
            for row, line in enumerate(table):
                for col, cell in enumerate(line):
                    if cell == 0:
                        continue
                    elif cell == 1:
                        blacks.append((row, col))
                    elif cell == 2:
                        whites.append((row, col))
                    else:
                        print("table 不合法")
                        return False
            for offset, loc in enumerate(blacks):
                self.move(loc)
                if offset < len(whites):
                    self.move(whites[offset])
            return True
        elif isinstance(records, list):
            for record in records:
                self.move(record)
            return True
        else:
            print("table 不合法")
            return False

    @timing
    def restart(self, forbidden=True, examinee=2):
        self.__init__(forbidden=forbidden, examinee=examinee)

    @timing
    def move(self, loc, show=True):
        # 检查能否落子
        if self.winner != 2:
            return False
        if max(loc) >= 15 or min(loc) < 0:
            logger.error("子落棋盘外")
            return False
        row, col = loc
        if self.table[row][col] != 2:
            logger.error(f"{loc}:这个位置已经有棋了")
            return False

        # 落子，更新棋盘
        player = B if self.step % 2 == 0 else W
        self.table[row][col] = player
        self.step += 1
        self.records.append(loc)
        self.zob_key ^= self.zob_grid[row][col][2] ^ self.zob_grid[row][col][player]

        attack = []
        if self.score[row][col][player] >= 3:
            attack = list(self.sub_score[loc[0]][loc[1]][player * 4: player * 4 + 4])
            if attack:
                self._winning(player, show=show, attack=attack)

        self._aoe_when_move_or_undo(row, col, show=show)

        return True

    @timing
    def undo(self):
        # 检查能否悔棋
        if not self.records:
            logger.error("悔棋失败！！！！！")
            raise TypeError

        # 悔棋，更新棋盘
        self.winner = 2
        self.step -= 1
        row, col = self.records.pop()
        tmp = self.table[row][col]

        self.zob_key ^= self.zob_grid[row][col][tmp] ^ self.zob_grid[row][col][2]
        self.table[row][col] = 2

        # 悔棋，更新局势
        self._aoe_when_move_or_undo(row, col)

    @timing
    def get_zob(self):
        if self.zob_key in self.translation_table:
            return self.translation_table[self.zob_key]
        else:
            return False

    def set_zob(self):
        self.translation_table[self.zob_key] = {
            "candidates": self.candidates.copy(),
            "score": self.score.copy(),
            "sub_score": self.sub_score.copy(),
            "forced": self.forced,
        }

    def show_situation(self):
        def get_chess(_row, _col):
            if self.table[_row][_col] == 2:
                return "   "
            elif self.table[_row][_col] == 1:
                return " W "
            else:
                return " B "

        def get_count(_a):
            return " " + str(_a) if _a <= 9 else str(_a)

        self._gen()
        print("黑方局势\t\t\t\t\t\t白方局势")
        header_line = "  | " + " ".join([get_count(i) for i in range(15)])
        print(header_line + "\t" + header_line)
        for row, line in enumerate(self.score):
            hei = get_count(row) + "| "
            bai = get_count(row) + "| "
            for col, (fir, sec) in enumerate(line):
                tmp_hei = get_count(fir) + " " if fir else get_chess(row, col)
                tmp_bai = get_count(sec) + " " if sec else get_chess(row, col)
                hei += tmp_hei
                bai += tmp_bai
            print(hei + "\t" + bai)
        print(self.candidates)


if __name__ == '__main__':
    b = BlackWhite()
    b.load(a)
    b.show_situation()
    show_timing()
