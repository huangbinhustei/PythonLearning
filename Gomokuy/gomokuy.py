#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from collections import Counter
import logging
from base import BaseGame, B, W, cost_count, PRINTING
from conf import a

ROADS = {0: (0, 1), 1: (1, 0), 2: (1, 1), 3: (1, -1)}
logger = logging.getLogger('Gomoku')
SCORE = {
    "活5": 100000,
    "活4": 100000,
    "冲5": 10000,
    "冲4": 10000,
    "活3": 1000,
    "冲3": 100,
    "活2": 10,
    "冲2": 1,
    "活1": 1,
    "冲1": 1,
}


class Gomokuy(BaseGame):
    def __init__(self, role=W, restart=False):
        super().__init__(self, restart=restart)
        self.values = {
            B: defaultdict(list),
            W: defaultdict(list),
        }
        self.lines = {
            B: [],
            W: [],
        }
        self.overdue_chess = []
        self.fresh_lines = {
            B: [],
            W: [],
        }
        self.role = role
        self.other = B if role == W else W

    def restart(self, role=W):
        super().restart()
        if role == B:
            self.going((7, 7))

    def base_linear(self, row, col, chess, direction, radio=False):
        def effect_area(_side, _offset):
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
                ret = effect_area(side, offset)
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
                    if radio:
                        self.overdue_chess.append([new_loc, direction])
                    break
        return line

    def __ending(self, loc, player, show=True):
        def make_fresh_line():
            self.overdue_chess = []
            self.fresh_lines = {
                B: [],
                W: [],
            }

            for direction in range(4):
                line = self.base_linear(loc[0], loc[1], player, direction, radio=True)
                if len(line["s"]) + len(line[-1]) + len(line[0]) + len(line[1]) >= 5:
                    self.fresh_lines[player].append(line)

        def checking_or_ending():
            self.check = []
            four_three_check = [0, 0]
            for line in self.fresh_lines[player]:
                counts = len(line["s"])
                if line[-1] and line[1]:
                    spaces = 2
                elif line[0] or line[1] or line[-1]:
                    spaces = 1
                else:
                    spaces = 0

                if counts == 5 and not line[0]:
                    self.win(player, info="五子棋胜", show=show)
                    break
                if counts == 4 and spaces == 2 and not line[0]:
                    self.win(player, info="四连胜", show=show)
                    break
                if counts > 5 and not line[0]:
                    info = "长连胜" if player == W else "长连禁手负"
                    self.win(player, info=info, show=show)
                    break
                if counts == 4 and spaces and len(line[0]) <= 1:
                    self.check += [line["s"]]
                    four_three_check[0] += 1
                if counts == 3 and spaces == 2 and len(line[0]) <= 1:
                    self.check += [line["s"]]
                    four_three_check[1] += 1
            self.check = sum(self.check, [])
            if four_three_check == [1, 1]:
                self.win(player, info="四三胜", show=show)
            elif four_three_check[0] >= 2:
                info = "四四胜" if player == W else "四四禁手负"
                self.win(player, info=info, show=show)
            elif four_three_check[1] >= 2:
                info = "三三胜" if player == W else "三三禁手负"
                self.win(player, info=info, show=show)

        make_fresh_line()
        checking_or_ending()

    def __init_all_lines(self):
        self.lines = {
            B: [],
            W: [],
        }
        for direction in range(4):
            checked = set([])
            for row in range(self.width):
                for col in range(self.width):
                    chess = self.table[row][col]
                    if not chess:
                        continue
                    if (row, col) in checked:
                        continue
                    line = self.base_linear(row, col, chess, direction)
                    checked |= set(line["s"])
                    if len(line["s"]) + len(line[-1]) + len(line[0]) + len(line[1]) < 5:
                        continue
                    self.lines[chess].append(line)
        self.__line_grouping(init_all=True)

    def __refresh_new_lines(self):
        def remove_old_lines():
            if not self.records:
                return
            last = self.records[-1]
            logger.info(f"last_player:{self.table[last[0]][last[1]]}, loc:{last}")
            ntd = []
            for sid, d in self.values.items():
                for k, lines in d.copy().items():
                    ret = [line for line in lines if last not in line]
                    if ret:
                        self.values[sid][k] = [line for line in lines if last not in line]
                    else:
                        ntd.append([sid, k])
            for sid, k in ntd:
                del self.values[sid][k]

        def add_new_lines():
            if not self.overdue_chess:
                return
            for loc, direction in self.overdue_chess:
                row, col = loc
                chess = self.table[row][col]
                line = self.base_linear(row, col, chess, direction)
                if len(line["s"]) + len(line[-1]) + len(line[0]) + len(line[1]) < 5:
                    continue
                self.fresh_lines[chess].append(line)
        remove_old_lines()
        add_new_lines()
        logger.info(self.fresh_lines)
        self.__line_grouping(init_all=False)

    def __line_grouping(self, init_all=True):
        if init_all:
            self.values = {
                B: defaultdict(list),
                W: defaultdict(list),
            }
            all_lines = self.lines
        else:
            all_lines = self.fresh_lines
        for sid, lines in all_lines.items():
            for line in lines:
                chang = min(5, len(line["s"] + line[0]))
                t = len(line["s"])
                t = "5" if t >= 5 else str(t)
                if line[-1] and line[1]:
                    key = "活" + t if len(line[0]) <= 1 else "冲" + t
                    range_att = min(max(0, 4 - chang), 2)
                    range_def = 1 if chang < 5 else 0
                    r = range_att if sid else range_def
                    line[-1] = line[-1][:r]
                    line[1] = line[1][:r]
                    format_line = line[-1] + line[0] + line[1]

                elif line[0] or line[1] or line[-1]:
                    key = "冲" + t
                    r = 5 - chang
                    line[-1] = line[-1][:r]
                    line[1] = line[1][:r]
                    format_line = line[-1] + line[0] + line[1]
                else:
                    continue
                self.values[sid][key].append(format_line)

    def going(self, loc, show=True):
        player = super().going(loc)
        if not player:
            return
        if show:
            logger.info(f"{self.step}\t:{PRINTING[player]}:{loc}")
        self.__ending(loc, player, show=show)

    def analyse(self):
        def win_chance_single_line():
            best_lines = []
            if "冲4" in player_chance or "活4" in player_chance or "活5" in player_chance or "冲5" in player_chance:
                if player == B:
                    best_lines = [player_chance[k] for k in ["冲4", "活4"] if k in player_chance]
                else:
                    best_lines = [player_chance[k] for k in ["冲4", "活4", "冲5", "活5"] if k in player_chance]
            elif "冲4" in opponent_chance or "活4" in opponent_chance or "活5" in opponent_chance or "冲5" in opponent_chance:
                if player == W:
                    best_lines = [opponent_chance[k] for k in ["冲4", "活4"] if k in opponent_chance]
                else:
                    best_lines = [opponent_chance[k] for k in ["冲4", "活4", "冲5", "活5"] if k in opponent_chance]
            elif "活3" in player_chance:
                best_lines = player_chance["活3"] if "活3" in player_chance else []
                best_lines = [best_lines]

            best_lines = sum(best_lines, [])

            return list(set(sum(best_lines, [])))

        def win_chance_mul_lines():
            my_3 = sum(player_chance["活2"], [])
            my_4 = sum(player_chance["冲3"], [])
            your_live_3 = sum(opponent_chance["活3"], [])

            my_33 = [item[0] for item in Counter(my_3).items() if item[1] > 1]
            my_44 = [item[0] for item in Counter(my_4).items() if item[1] > 1]
            my_43 = [item for item in my_4 if item in my_3]

            if player == B:
                # 针对黑棋，自己的四三 > 对方的活三
                attack = [item for item in my_43 if item not in my_44 + my_33] or your_live_3
                # todo: 43不能在同一行，比如 0 1 1 1 0 0 1 0 0，此时电脑会判断中间两个0能够组成43胜，但是其实是长连禁手
            else:
                # 针对白棋，自己四四或四三 > 对方的活三 > 自己的三三，都没有实际上返回的是 False
                attack = my_44 + my_43 or your_live_3 or my_33

            if attack:
                ret = list(set(attack))
            else:
                # 假如没有进攻，就被迫开始防守
                your_3 = sum(opponent_chance["活2"], [])
                your_4 = sum(opponent_chance["冲3"], [])
                your_33 = [item[0] for item in Counter(your_3).items() if item[1] > 1]
                your_44 = [item[0] for item in Counter(your_4).items() if item[1] > 1]
                your_43 = [item for item in your_4 if item in your_3]
                if player == B:
                    fir = your_44 + your_43
                    sec = your_33 + my_4 + my_3
                else:
                    fir = [item for item in your_43 if item not in your_44 + your_33]
                    sec = your_33 + my_4 + my_3
                defence = fir if fir else sec
                ret = list(set(defence))
            return ret

        def normal_chance():
            # 从["冲3", "活2", "冲2", "冲1", "活1"]中选择
            temp = [i[j] for i in (player_chance, opponent_chance) for j in ("冲3", "活2", "冲2", "冲1", "活1")]
            ret = list(set(sum(sum(temp, []), [])))
            return ret

        if self.winner:
            return False
        player = W if self.step % 2 else B
        opponent = W if player == B else B

        self.__refresh_new_lines()
        # self.__init_all_lines()

        player_chance = self.values[player]
        opponent_chance = self.values[opponent]
        logger.info(self.values)

        return win_chance_single_line() or win_chance_mul_lines() or normal_chance()

    def min_max_search(self, DEEPS=5):
        def win_or_lose(deeps):
            if not self.winner:
                if deeps == 0:
                    my_score = sum([SCORE[key] * len(v) for (key, v) in self.values[self.role].items()])
                    your_score = sum([SCORE[key] * len(v) for (key, v) in self.values[self.other].items()])
                    return my_score - your_score
                else:
                    poss = self.analyse()
                    player = B if self.step % 2 else W
                    if not poss:
                        return False
                    result = [0] * len(poss)
                    for ind, pos in enumerate(poss):
                        self.going(pos, show=False)
                        if deeps == DEEPS:
                            new_deeps = deeps - 1 if len(poss) > 1 else 0
                        else:
                            new_deeps = deeps - 1
                        temp_score = win_or_lose(new_deeps)
                        result[ind] = temp_score
                        self.undo()
                        if temp_score == 9999999 and player == self.role:
                            # 轮到自己，且某一步可以自己赢
                            break
                        elif temp_score == -9999999 and player != self.role:
                            # 轮到对方走，且某一步可以对方赢
                            break
                    if deeps == DEEPS:
                        return result, poss
                    elif player == self.role:
                        return max(result)
                    else:
                        return min(result)
            elif self.winner == self.role:
                return 9999999
            else:
                return -9999999

        if self.winner:
            return False

        self.__init_all_lines()
        self.__line_grouping()
        fin_result, fin_poss = win_or_lose(DEEPS)
        logger.info(f"poss=\t{fin_poss}")
        logger.info(f"result=\t{fin_result} best={fin_poss[fin_result.index(max(fin_result))]}")
        return fin_poss[fin_result.index(max(fin_result))]


@cost_count
def bag():
    g = Gomokuy()
    g.parse(a)
    g.min_max_search(DEEPS=10)

if __name__ == '__main__':
    bag()
