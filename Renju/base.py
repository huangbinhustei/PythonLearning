#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import wraps
import time
import logging
from collections import defaultdict
import numpy as np


logger = logging.getLogger('Renju')
logger.addHandler(logging.StreamHandler())

B = 0  # 黑方
W = 1  # 白方
N = 2  # 空
WIN = 9999999
LOSE = -9999999
PRINTING = ("黑","白")
cost_dict = defaultdict(lambda: [0, 0.0])
ROADS = ((0, 1), (1, 0), (1, 1), (1, -1))
LC = [
    # 两边空    左边被堵   右边被堵  两边被堵
    ["00000", "00000", "00000", "00000"],   # 00000
    ["00020", "00020", "00010", "00010"],   # 00001
    ["00202", "00202", "00201", "00101"],   # 00010
    ["34400", "34400", "33300", "33300"],   # 00011
    ["02020", "02020", "02020", "01010"],   # 00100
    ["34040", "34040", "33030", "33030"],   # 00101
    ["44004", "34004", "34003", "33003"],   # 00110
    ["56000", "56000", "55000", "55000"],   # 00111
    ["20200", "10200", "20200", "10100"],   # 01000
    ["30440", "30440", "30330", "30330"],   # 01001
    ["40404", "30404", "40403", "30303"],   # 01010
    ["50600", "50600", "50500", "50500"],   # 01011
    ["40044", "30043", "40043", "30033"],   # 01100
    ["50060", "50060", "50050", "50050"],   # 01101
    ["60006", "50006", "60005", "50005"],   # 01110
    ["80000", "80000", "80000", "80000"],   # 01111
    ["02000", "01000", "02000", "01000"],   # 10000
    ["03330", "03330", "03330", "03330"],   # 10001
    ["04403", "03303", "04403", "03303"],   # 10010
    ["05500", "05500", "05500", "05500"],   # 10011
    ["04043", "03033", "04043", "03033"],   # 10100
    ["05050", "05050", "05050", "05050"],   # 10101
    ["06005", "05005", "06005", "05005"],   # 10110
    ["08000", "08000", "08000", "08000"],   # 10111
    ["00443", "00333", "00443", "00333"],   # 11000
    ["00550", "00550", "00550", "00550"],   # 11001
    ["00605", "00505", "00605", "00505"],   # 11010
    ["00800", "00800", "00800", "00800"],   # 11011
    ["00065", "00055", "00065", "00055"],   # 11100
    ["00080", "00080", "00080", "00080"],   # 11101
    ["00008", "00008", "00008", "00008"],   # 11110
    ["00000", "00000", "00000", "00000"]    # 11111
]

score_in_sc = (16,8,4,2,1)


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
    logger.info("\nTiming\n+-%-24s-+-%-12s-+-%-8s-+" % ("-" * 24, "-" * 12, "-" * 8))
    logger.info("| %-24s | %-12s | %-8s |" % ("Func name", "Times", "Cost(ms)"))
    logger.info("+-%-24s-+-%-12s-+-%-8s-+" % ("-" * 24, "-" * 12, "-" * 8))
    for k, v in cost_dict.items():
        logger.info("| %-24s | %-12d | %-8s |" % (k, v[0], str(int(v[1] * 1000))))
    logger.info("+-%-24s-+-%-12s-+-%-8s-+\n" % ("-" * 24, "-" * 12, "-" * 8))


@timing
def four_to_one(tmp):
    return [max(tmp[0: 4]), max(tmp[4: 8])]


class BlackWhite:
    def __init__(self, forbidden=True):
        self.step = 0
        self.records = []
        self.winner = 2
        self.forbidden = forbidden
        self.dangerous = []  # 将军的棋子
        self.forced = False  # 自己这一步是否是被迫走的

        self.table = np.array([[N] * 225]).reshape(15, 15)
        self.score = np.array([[0] * 450]).reshape(15, 15, 2)
        self.sub_score = np.array([[0] * 1800]).reshape(15, 15, 8)

        self.candidates = []

        self.zob_grid = []
        self.zob_key = 0
        ra = 2 ** 105
        self.zob_grid = np.random.uniform(0, ra, size=(15, 15, 3))
        self.translation_table = dict()

        self.ways = init_ways()

    def _winning(self, sid, line=False, show=True, attack=[]):
        def declaring(p, information):
            self.winner = p
            if show:
                logger.info(f"{PRINTING[sid]}方{information}")

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
            def blocking_four_three():
                # 用于防守伪四三胜
                direction = attack.index(5)
                last_pos = self.records[-1]
                four_range = []
                for j in (-1, 1):
                    for i in range(1, 5):
                        pos = (last_pos[0] + ROADS[direction][0] * i * j,
                               last_pos[1] + ROADS[direction][1] * i * j)
                        if min(pos) < 0:
                            continue
                        if max(pos) > 14:
                            continue
                        if self.table[pos[0]][pos[1]] == N and chance_of_mine[pos[0]][pos[1]] == 5:
                            four_range.append(pos)
                        elif self.table[pos[0]][pos[1]] == sid:
                            continue
                        else:
                            break

                return [pos for pos in four_range
                        if self.table[pos[0]][pos[1]] == N
                        and chance_of_your[pos[0]][pos[1]] >= 5]

            opt = W if sid == B else B
            chance_of_your = self.score[:, :, opt]
            chance_of_mine = self.score[:, :, sid]
            best_score_your = np.max(chance_of_your)

            if 6 in attack:
                # 构成活四
                if best_score_your < 9:
                    # 只要对方当前没有冲四，就获胜
                    declaring(sid, "四连胜")
            elif attack.count(5) >= 2:
                if sid == B:
                    declaring(W, "禁手负")
                else:
                    declaring(W, "获胜")
            elif attack.count(4) >= 2:
                if sid == B:
                    declaring(W, "禁手负")
                elif best_score_your < 5:
                    # 三三时只要对方有冲四就不能算赢
                    declaring(W, "获胜")

            elif 5 in attack and 4 in attack:
                counterattack = blocking_four_three()
                if not counterattack:
                    declaring(sid, "四三胜")

        if line:
            _win_by_line()
        elif attack:
            _win_by_attack()

    @timing
    def old_situation_updater(self, row, col, show=True):
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
                chess_type_index_of_lc = 0
                for item in chesses[::-1]:
                    if item != 2:
                        chess_type_index_of_lc += rate
                    rate *= 2
                return chess_type_index_of_lc

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
            def line_cutter(_line):
                ret = []
                flag = _line[0]
                tmp = [flag]
                for x in _line[1:]:
                    if x == flag:
                        tmp.append(x)
                    else:
                        ret.append(tmp)
                        tmp = [x]
                        flag = x
                ret.append(tmp)
                return ret

            def line_grouper(_line):
                ret = line_cutter(_line)

                fin = set([0])
                offset = 0
                for ind, line in enumerate(ret):
                    lg = len(line)
                    if line[0] == 2:
                        offset += lg
                        continue
                    if ind > 0 and ret[ind - 1][0] == 2:
                        start = offset - 5 + lg
                        if start >= 0:
                            fin.add(start)
                    if ind < len(ret) - 1 and ret[ind + 1][0] == 2:
                        fin.add(offset)
                    if lg >= 5:
                        fin.add(offset)
                    offset += lg
                fin = [line_input[i: i + 5] for i in fin]
                return fin

            inp = [self.table[row][col] for row, col in line_input]
            return line_grouper(inp)

        ret = []
        changes = dict()
        self.sub_score[row][col] = [0, 0, 0, 0, 0, 0, 0, 0]

        aoe_line = self.ways[row * 15 + col]
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
                self.score[row][col] = four_to_one(values)

        self._gen()
        self.set_zob()

    @timing
    def _situation_updater(self, row, col, show=True):
        changes = set([])
        aoe_line = self.ways[row * 15 + col]

        for direction in range(4):
            tmp_line = aoe_line[direction]
            for x, y in tmp_line:
                self.sub_score[x][y][direction] = 0
                self.sub_score[x][y][direction + 4] = 0
                changes.add((x, y))

            _index = 0
            while _index < len(tmp_line) - 4:
                last = N
                chess_type_index_of_lc = 0
                for j in range(5):
                    this_row, this_col = tmp_line[_index + j]
                    this_cell = self.table[this_row][this_col]
                    if this_cell == N:
                        # 全部为空，什么操作都不做
                        continue
                    else:
                        if last == N:
                            # 之前有棋，现在为空，开始计分
                            last = this_cell
                            chess_type_index_of_lc += score_in_sc[j]
                        elif last == this_cell:
                            # 现在的棋和之前的棋相同，继续积分
                            chess_type_index_of_lc += score_in_sc[j]
                        else:
                            # 现在的棋和之前的棋不同，不在积分，且可以跳格。
                            _index += j
                            break
                else:
                    # 假如 no break，表示没有跳格
                    if last == N:
                        _index += 1
                        continue
                    changed_locations = tmp_line[_index: _index + 5]

                    if chess_type_index_of_lc == 31:
                        # 5 连了
                        self._winning(last, line=changed_locations, show=show)

                    opt = B if last == W else W
                    if _index == 0:
                        left = False
                    else:
                        side_row, side_col = tmp_line[_index - 1]
                        left = False if self.table[side_row][side_col] == opt else True
                    if _index + 5 == len(tmp_line):
                        right = False
                    else:
                        side_row, side_col = tmp_line[_index + 5]
                        right = False if self.table[side_row][side_col] == opt else True

                    if left:
                        block = 0 if right else 2
                    else:
                        block = 1 if right else 3
                    
                    offset = last * 4 + direction
                    for ind, (row, col) in enumerate(changed_locations):
                        self.sub_score[row][col][offset] = max(
                            self.sub_score[row][col][offset],
                            int(LC[chess_type_index_of_lc][block][ind]))

                    _index += 1

        for change_row, change_col in changes:
            self.score[change_row][change_col] = four_to_one(self.sub_score[change_row][change_col])

        self._gen()
        self.set_zob()

    @timing
    def _aoe(self, row, col, show=True):
        # 不管是下棋还是悔棋，这些都是受影响的区域，需要重新计算结果
        zob = self.get_zob()
        if zob:
            self.candidates = zob["candidates"].copy()
            self.score = zob["score"].copy()
            self.sub_score = zob["sub_score"].copy()
            self.forced = zob["forced"]
        else:
            self._situation_updater(row, col, show=show)

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
                        logger.error("table 不合法")
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
            logger.error("table 不合法")
            return False

    def restart(self, forbidden=True):
        self.__init__(forbidden=forbidden)

    @timing
    def move(self, loc, show=True):
        # 检查能否落子
        if self.winner != 2:
            logger.info("胜负已分！")
            return False
        if max(loc) >= 15 or min(loc) < 0:
            logger.error("子落棋盘外")
            return False
        row, col = loc
        if self.table[row][col] != N:
            logger.error(f"{loc}:这个位置已经有棋了")
            return False

        # 落子，更新棋盘
        player = B if self.step % 2 == 0 else W
        self.table[row][col] = player
        self.step += 1
        self.records.append(loc)
        self.zob_key ^= int(self.zob_grid[row][col][2]) ^ int(self.zob_grid[row][col][player])

        if self.score[row][col][player] >= 3:
            attack = list(self.sub_score[loc[0]][loc[1]][player * 4: player * 4 + 4])
            if attack:
                self._winning(player, show=show, attack=attack)

        self._aoe(row, col, show=show)

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

        self.zob_key ^= int(self.zob_grid[row][col][tmp]) ^ int(self.zob_grid[row][col][2])
        self.table[row][col] = N

        # 悔棋，更新局势
        self._aoe(row, col)

    @timing
    def get_zob(self):
        if self.zob_key in self.translation_table:
            return self.translation_table[self.zob_key]
        else:
            return False

    @timing
    def set_zob(self):
        self.translation_table[self.zob_key] = {
            "candidates": self.candidates.copy(),
            "score": self.score.copy(),
            "sub_score": self.sub_score.copy(),
            "forced": self.forced,
        }

    def show_situation(self):
        def get_chess(_row, _col):
            if self.table[_row][_col] == N:
                return "   "
            elif self.table[_row][_col] == W:
                return " W "
            else:
                return " B "

        def get_count(_a):
            return " " + str(_a) if _a <= 9 else str(_a)

        self._gen()
        logger.info("黑方局势\t\t\t\t\t\t白方局势")
        header_line = "  | " + " ".join([get_count(i) for i in range(15)])
        logger.info(header_line + "\t" + header_line)
        for row, line in enumerate(self.score):
            hei = get_count(row) + "| "
            bai = get_count(row) + "| "
            for col, (fir, sec) in enumerate(line):
                tmp_hei = get_count(fir) + " " if fir else get_chess(row, col)
                tmp_bai = get_count(sec) + " " if sec else get_chess(row, col)
                hei += tmp_hei
                bai += tmp_bai
            logger.info(hei + "\t" + bai)
        logger.info(self.candidates)


class Renjuy(BlackWhite):
    def __init__(self, forbidden=True):
        BlackWhite.__init__(self, forbidden=forbidden)
        self.player = 2

    def probe(self, loc, show=True):
        ret = BlackWhite.move(self, loc, show=show)
        if not ret:
            self.show_situation()
            logger.error(f"{loc}落子失败！\tself.winner = {self.winner}\nrecords = {self.records}")
            raise RuntimeError

    def get_score(self):
        if self.player == 2:
            logger.error("初始化失败")
            raise RuntimeError
        else:
            if self.winner == 2:
                opt_player = B if self.player == W else W
                chance_of_mine = self.score[:, :, self.player]
                chance_of_your = self.score[:, :, opt_player]
                return np.sum(chance_of_mine) - np.sum(chance_of_your)
            elif self.winner == self.player:
                return WIN
            else:
                return LOSE

    def min_max(self, max_deep=3):
        def alpha_beta(deep, p, alpha, beta):
            if p:
                situation = LOSE
                for i in self.candidates:
                    self.probe(i, show=False)
                    if self.winner == self.player:
                        situation = WIN
                    elif self.winner != 2:
                        situation = LOSE
                    # 上面两个条件，分出胜负了，直接打分，不用进入下一层
                    elif deep == max_deep:
                        # 上面这个条件，没有分出胜负但是已经深度够了，直接打分，也不进入下一层
                        situation = self.get_score()
                    else:
                        situation = max(situation, alpha_beta(deep, False, alpha, beta))
                    alpha = max(alpha, situation)
                    self.undo()
                    if situation == WIN:
                        self.translation_table[self.zob_key]["candidates"] = [i]
                    if beta <= alpha:
                        break
            else:
                situation = WIN
                for i in self.candidates:
                    self.probe(i, show=False)
                    if self.winner == self.player:
                        situation = WIN
                    elif self.winner != 2:
                        situation = LOSE
                    # 上面两个条件，分出胜负了，直接打分，不用进入下一层
                    elif deep == max_deep:
                        # 上面这个条件，没有分出胜负但是已经深度够了，直接打分，也不进入下一层
                        situation = self.get_score()
                    else:
                        if self.forced:
                            # 假如下一步，黑方是被迫走的，那么不算深度
                            situation = min(situation, alpha_beta(deep, True, alpha, beta))
                        else:
                            situation = min(situation, alpha_beta(deep + 1, True, alpha, beta))
                    beta = min(beta, situation)
                    self.undo()
                    # if situation == LOSE:
                    #     self.translation_table[self.zob_key]["candidates"] = [i]
                    if beta <= alpha:
                        break

            return situation

        if self.forced:
            best_choice = self.candidates[0]
            return best_choice, 0, self.candidates, [0, 0]
        else:
            result = []
            for candidate in self.candidates:
                self.probe(candidate, show=False)
                if self.winner == self.player:
                    exam = WIN
                elif self.winner != 2:
                    exam = LOSE
                else:
                    exam = alpha_beta(0, False, LOSE, WIN)
                result.append(exam)
                self.undo()
                if exam == WIN:
                    break

            best_choice = self.candidates[result.index(max(result))]
            return best_choice, max(result), self.candidates, result

    @timing
    def iterative_deepening(self, max_deep):
        self.player = W if self.step % 2 else B

        for d in range(1, max_deep + 1):
            logger.debug(f"迭代深度：{d}")
            pos, fen, fin_poss, fin_result = self.min_max(max_deep=d)
            if fen == WIN:
                logger.debug(f"break in iterative_deepening @ deep = {d}")
                break

        logger.debug(f"result：{fin_result}")
        logger.debug(f"poss  ：{fin_poss}")
        logger.debug(f"best  ： {pos} when step is {self.step}")

        return pos
