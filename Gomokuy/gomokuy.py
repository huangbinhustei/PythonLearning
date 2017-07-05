#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from base import BaseGame, B, W, cost_count
from conf import a
from random import choice
from collections import Counter
import logging


logger = logging.getLogger('Gomoku')
SCORE = {
    "活5": 100000,
    "冲5": 100000,
    "活4": 100000,
    "冲4": 10000,
    "活3": 1000,
    "冲3": 100,
    "活2": 10,
    "冲2": 1,
    "活1": 1,
    "冲1": 1,
    }


class Gomokuy(BaseGame):
    def __init__(self):
        BaseGame.__init__(self)
        self.values = dict()
        self.lines = {
            B: [],
            W: [],
        }

    def inside_make_line(self):
        self.values = {
            B: defaultdict(list),
            W: defaultdict(list),
        }
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
        self.inside_line_grouping()

    def inside_line_grouping(self):
        for sid, lines in self.lines.items():
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

        self.inside_make_line()

        player_chance = self.values[player]
        opponent_chance = self.values[opponent]

        return win_chance_single_line() or win_chance_mul_lines() or normal_chance()

    @cost_count
    def min_max_search(self, DEEPS=5):
        def _logging(_pos, _deeps):
            if _deeps == DEEPS:
                logger.debug(f"The first step is {_pos}")

        def new_win_or_lose(deeps, t_max=-99999999, t_min=99999999):
            print("hehe", file=f)
            if not self.winner:
                if deeps == 0:
                    my_score = sum([SCORE[key] * len(v) for (key, v) in self.values[player].items()])
                    your_score = sum([SCORE[key] * len(v) for (key, v) in self.values[opponent].items()])
                    return my_score - your_score
                else:
                    poss = self.analyse()
                    if not poss:
                        return False
                    result = [0] * len(poss)
                    next_player = B if (self.step + 1) % 2 == 1 else W
                    if deeps == DEEPS:
                        new_deeps = deeps - 1 if len(poss) > 1 else 0
                    else:
                        new_deeps = deeps - 1
                    if next_player != player:
                        # max层，返回这一层的最大值
                        for ind, pos in enumerate(poss):
                            _logging(pos, deeps)
                            self.move(pos)
                            v = new_win_or_lose(new_deeps,t_max=t_max, t_min=t_min)
                            # v是下一层的分，下一层一定是返回最小值
                            # 假如某个最小值比现在的最大值小，那么他一定会选这个最小的值，所以这个点的下一层就不用算了。
                            t_max = max(t_max, v)
                            result[ind] = v
                            self.undo()

                            if t_min <= t_max:
                                break
                        if deeps == DEEPS:
                            # 假如是顶层，返回所有选项 & 分值
                            return result, poss
                        else:
                            return v
                    else:
                        # min层，返回这一层的最小值
                        v = 9999999
                        for ind, pos in enumerate(poss):
                            _logging(pos, deeps)
                            self.move(pos)
                            v = new_win_or_lose(new_deeps,t_max=t_max, t_min=t_min)
                            t_min = min(t_min, v)
                            result[ind] = v
                            self.undo()
                            if t_min <= t_max:
                                break
                        if deeps == DEEPS:
                            return result, poss
                        else:
                            return v
            elif self.winner == player:
                return 9999999
            else:
                return -9999999

        def win_or_lose(deeps):
            print("haha", file=f)
            if not self.winner:
                if deeps == 0:
                    my_score = sum([SCORE[key] * len(v) for (key, v) in self.values[player].items()])
                    your_score = sum([SCORE[key] * len(v) for (key, v) in self.values[opponent].items()])
                    return my_score - your_score
                else:
                    poss = self.analyse()
                    if not poss:
                        return False

                    result = [0] * len(poss)
                    next_player = B if (self.step + 1) % 2 == 1 else W
                    for ind, pos in enumerate(poss):
                        _logging(pos, deeps)
                        self.move(pos)
                        if deeps == DEEPS:
                            new_deeps = deeps - 1 if len(poss) > 1 else 0
                        else:
                            new_deeps = deeps - 1
                        temp_score = win_or_lose(new_deeps)
                        result[ind] = temp_score
                        self.undo()
                        if temp_score == 9999999 and next_player == player:
                            # 轮到自己，且某一步可以自己赢
                            break
                        elif temp_score == -9999999 and next_player != player:
                            # 轮到对方走，且某一步可以对方赢
                            break
                    if deeps == DEEPS:
                        return result, poss
                    elif next_player == player:
                        return max(result)
                    else:
                        return min(result)
            elif self.winner == player:
                return 9999999
            else:
                return -9999999

        if self.winner:
            return False

        f = open("/Users/baidu/Documents/百度/Git/PythonLearning/Gomokuy/1.txt" , "w")
        player = W if self.step % 2 else B
        opponent = W if player == B else B
        fin_result, fin_poss = win_or_lose(DEEPS)
        best_choice = fin_poss[fin_result.index(max(fin_result))]
        logger.info(f"result：{fin_result}")
        logger.info(f"poss  ：{fin_poss}")
        logger.info(f"best  ： {best_choice}")
        f.close()
        return best_choice


if __name__ == '__main__':
    g = Gomokuy()
    g.parse(a)
    g.min_max_search(DEEPS=10)
