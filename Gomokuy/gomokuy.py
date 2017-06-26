#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from base import BaseGame, B, W
from conf import a, SCORE, cost_count
from random import choice


class Gomokuy(BaseGame):
    def __init__(self):
        BaseGame.__init__(self)
        self.values = dict()
        self.lines = {
            True: [],
            False: [],
        }

    def inside_make_line(self):
        for direction in range(4):
            checked = set([])
            for row in range(self.width):
                for col in range(self.width):
                    chess = self.table[row][col]
                    if not chess:
                        continue
                    if (row, col) in checked:
                        continue
                    line = {
                        "s": [(row, col)],
                        0: [],  # 中间的缝隙
                        -1: [],  # 某一边的空
                        1: [],  # 另一边的空
                    }
                    ret = self.inside_make_line_for_single_chessman(row, col, chess, direction, line)
                    checked |= ret

    def inside_make_line_for_single_chessman(self, row, col, chess, direction, line):
        for side in (-1, 1):
            for offset in range(1, 9):
                ret = self.inside_new_cell_loc(row, col, direction, side, offset)
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
        self.inside_line_merge(line, chess)
        return set(line["s"])

    def inside_line_merge(self, line, chess):
        line[-1] = line[-1][:5 - len(line["s"])]
        line[1] = line[1][:5 - len(line["s"])]
        me = B if (self.step + 1) % 2 == 1 else W
        if len(line["s"]) + len(line[-1]) + len(line[0]) + len(line[1]) < 5:
            return
        self.lines[chess == me].append(line)

    # @cost_count
    def analyse(self, single_step=True):
        def make_pos_group(key_group):
            key_group = set([SCORE[k] for k in key_group])
            attack = sum([self_chance[k] for k in key_group], [])
            defence = sum([opponent_chance[k] for k in key_group], [])
            return attack if attack else defence

        self.values = dict()
        self.lines = {
            True: [],
            False: [],
        }
        self.inside_make_line()
        for sid, lines in self.lines.items():
            status = defaultdict(int)
            for line in lines:
                chang = 5 - len(line[0]) if len(line["s"]) + len(line[0]) > 5 else len(line["s"])
                if line[-1] and line[1]:
                    key = "活" + str(chang)
                    if not line[0]:
                        r = {1: 1, 2: 2, 3: 1, 4: 1}[chang]
                        line[-1] = line[-1][:r]
                        line[1] = line[1][:r]
                    else:
                        # 进攻和防守的区域是不一样的。
                        r = {1: 1, 2: 1, 3: 0, 4: 0}[chang] if sid else {1: 1, 2: 1, 3: 1, 4: 0}[chang]
                        line[-1] = line[-1][:r]
                        line[1] = line[1][:r]
                elif line[0] or line[1] or line[-1]:
                    key = "冲" + str(chang)
                    if not line[0]:
                        r = {1: 1, 2: 3, 3: 2, 4: 1}[chang]
                        line[-1] = line[-1][:r]
                        line[1] = line[1][:r]
                    else:
                        r = {1: 1, 2: 2, 3: 1, 4: 0}[chang]
                        line[-1] = line[-1][:r]
                        line[1] = line[1][:r]
                else:
                    continue

                base_score = SCORE[key] if key in SCORE else 0
                for k in (-1, 0, 1):
                    for loc in line[k]:
                        status[loc] = max(base_score, status[loc])
            temp = defaultdict(list)
            for loc, score in status.items():
                temp[score].append(loc)
            self.values[sid] = temp

        self_chance = self.values[True]
        opponent_chance = self.values[False]
        if SCORE["冲4"] in self_chance:
            best_pos_group = self_chance[SCORE["冲4"]]
        elif SCORE["冲4"] in opponent_chance:
            best_pos_group = opponent_chance[SCORE["冲4"]]
        elif SCORE["活3"] in self_chance:
            best_pos_group = self_chance[SCORE["活3"]]
        elif SCORE["活3"] in opponent_chance:
            best_pos_group = self_chance[SCORE["冲3"]]
            best_pos_group += opponent_chance[SCORE["活3"]]
        else:
            temp_1 = make_pos_group(["活2", "冲3"])
            best_pos_group = temp_1 if temp_1 else make_pos_group(["冲2", "活1", "冲1"])

        best_pos_group = list(set(best_pos_group))
        single = choice(best_pos_group)
        mul = best_pos_group
        ret = single if single_step else mul
        return ret

    def temp(self, me, deeps):
        def logging(_pos, _deeps):
            if _deeps == DEEPS:
                print(f"\nThe first step is {_pos}")

        if not self.winner:
            if deeps == 0:
                return 0
            else:
                poss = self.analyse(single_step=False)
                result = [0] * len(poss)
                for ind, pos in enumerate(poss):
                    logging(pos, deeps)
                    self.going(pos)
                    temp_score = self.temp(me, deeps - 1)
                    result[ind] = temp_score
                    self.ungoing()
                    next_player = B if (self.step + 1) % 2 == 1 else W
                    if temp_score == 1 and next_player == me:
                        # 轮到自己，且某一步可以自己赢
                        break
                    elif temp_score == -1 and next_player != me:
                        # 轮到对方走，且某一步可以对方赢
                        # 这里剪枝有问题，禁手不算，并且禁手明明是黑棋自己走出的，不应该出现剪刀
                        break
                if deeps == DEEPS:
                    print(poss)
                    print(max(result))
                    return result
                elif deeps % 2 == 0:
                    return max(result)
                else:
                    return min(result)
        elif self.winner == me:
            return 1
        else:
            return -1

    @cost_count
    def mul(self):
        me = B if (self.step + 1) % 2 == 1 else W
        print(self.temp(me, DEEPS))


if __name__ == '__main__':
    DEEPS = 5
    g = Gomokuy()
    g.parse(a)
    g.mul()
    # print(g.analyse(single_step=False))
    # print(g._ending((7, 3), B))
