#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from base import BaseGame, B, W, cost_count, PRINTING
from conf import a
from random import choice
from collections import Counter, defaultdict
import logging
from time import time


step = []
logger = logging.getLogger('Gomoku')
logger.setLevel(logging.DEBUG)
ROADS = {0: (0, 1), 1: (1, 0), 2: (1, 1), 3: (1, -1)}
ADR = {
    0: {
        "冲1":1, "冲2":2, "冲3":2, "冲4":1, "冲5":0, "冲6":0,
        "活1":1, "活2":1, "活3":2, "活4":1, "活5":0, "活6":0},
    1: {
        "冲1":1, "冲2":2, "冲3":1, "冲4":0, "冲5":0, "冲6":0,
        "活1":1, "活2":1, "活3":1, "活4":0, "活5":0, "活6":0},
    2: {
        "冲1":1, "冲2":1, "冲3":0, "冲4":0, "冲5":0, "冲6":0,
        "活1":1, "活2":1, "活3":0, "活4":0, "活5":0, "活6":0},
    }
SCORE = {
    "活6": 100000,
    "冲6": 100000,
    "活5": 100000,
    "冲5": 100000,
    "活4": 100000,
    "冲4": 1000,
    "活3": 1000,
    "冲3": 10,
    "活2": 10,
    "冲2": 1,
    "活1": 1,
    "冲1": 1,
    }
func_count = 0


class Gomokuy(BaseGame):
    def __init__(self, settle=False):
        BaseGame.__init__(self)
        self.values = dict()
        self.check = []
        self.forbidden = [0, 0]
        self.settle = settle

    def base_linear(self, row, col, chess, direction):
        line = {
            "s": [(row, col)],
            0: [],  # 中间的缝隙
            -1: [],  # 某一边的空
            1: [],  # 另一边的空
        }
        for side in (-1, 1):
            for offset in range(1, 9):
                new_row = row + offset * side * ROADS[direction][0]
                new_col = col + offset * side * ROADS[direction][1]
                if new_row >= self.width or new_row < 0:
                    break
                if new_col >= self.width or new_col < 0:
                    break

                new_cell = self.table[new_row][new_col]
                new_loc = (new_row, new_col)

                if new_cell == 0:
                    line[side].append(new_loc)
                elif new_cell == chess:
                    if line[side]:
                        if line[0]:
                            break
                        else:
                            if len(line[side]) <= 1:
                                line[0] = line[side]
                                line[side] = []
                            else:
                                break
                    line["s"].append(new_loc)
                else:
                    break
        return line

    def inside_make_line(self):
        self.values = {
            B: defaultdict(list),
            W: defaultdict(list),
        }
        self.check = []
        self.forbidden = [0, 0]
        last_move = self.records[-1] if self.records else "nothing"

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
                    self.inside_line_grouping(line, chess, last_move)

    def inside_line_grouping(self, line, sid, last_move):
        t = len(line["s"])
        t = 6 if t >= 6 else t
        if line[-1] and line[1]:
            key = "活" + str(t) if t + len(line[0]) <= 4 else "冲" + str(t)
            if t >= 4:
                self.check += line["s"]
            elif t == 3 and len(line[0]) <= 1:
                self.check += line["s"]
            if last_move in line["s"]:
                if t == 3 and len(line[0]) <= 1:
                    self.forbidden[0] += 1
                elif t == 4:
                    self.forbidden[1] += 1
        elif line[0] or line[1] or line[-1]:
            key = "冲" + str(t)
            if t >= 4:
                self.check += line["s"]
            if t == 4 and last_move in line["s"]:
                self.forbidden[1] += 1
        line[-1] = line[-1][:ADR[len(line[0])][key]]
        line[1] = line[1][:ADR[len(line[0])][key]]
        format_line = line[-1] + line[0] + line[1]
        self.values[sid][key].append(format_line)

    def move(self, loc, show=True):
        super().move(loc, show=show)
        self.analyse(show=show)

    def win_announce(self, show=True):
        info = ""
        for _player in (B, W):
            _opt = B if _player == W else W

            if self.values[_player]["活6"]:
                self.winner = W
                info = "白·长连·胜" if _player == W else "黑·长连禁手·负"
            elif self.values[_player]["活5"]:
                self.winner = _player
                info = PRINTING[_player] + "·五连·胜"
            elif self.forbidden[1] >= 2:
                    self.winner = W
                    info = "白·四四·胜" if _player == W else "黑·四四禁手·负"
                # else:
                #     # 不相交的不是禁手
                #     self.winner = _player
                #     info = PRINTING[_player] + "·四四·胜"
            elif self.values[_player]["活4"]:
                self.winner = _player
                info = PRINTING[_player] + "·四连·胜"
            elif len(self.values[_player]["活3"]) >= 2:
                if self.forbidden[0] >= 2:
                    self.winner = W
                    info = "黑·三三禁手·负"
                if self.values[_opt]["活3"] or self.values[_opt]["冲3"] or self.values[_opt]["冲4"]:
                    # 对方还可以防御
                    continue
                # else:
                #     # todo: 这种似乎不叫三三胜，上面的四四胜也是同理
                #     self.winner = _player
                #     info = PRINTING[_player] + "·三三·胜"
            elif len(self.values[_player]["活4"]) + len(self.values[_player]["冲4"]) + len(self.values[_player]["活3"]) >= 2:
                def_poss = sum(self.values[_player]["活4"] + self.values[_player]["冲4"], [])
                att_poss = sum(self.values[_opt]["活3"] + self.values[_opt]["冲3"], [])
                if not [p for p in def_poss if p in att_poss]:
                    self.winner = _player
                    info = PRINTING[_player] + "·四三·胜"
        
        if not self.winner:
            return
        if show:
            logger.info(f"{self.records}\t{info}")
        else:
            logger.debug(f"{self.records}\t{info}")

    def analyse(self, show=True):
        def win_chance_single_line():
            # 自己有冲四、活四 -> 对方的冲四、活四 -> 自己的活三
            B_chance = [i for i in ["冲4", "活4"] if i in self.values[B]]
            W_chance = [i for i in ["冲4", "活4", "冲5", "活5", "冲6", "活6"] if i in self.values[W]]

            # first_choice:走了直接赢
            first_choice = [player_chance[k] for k in B_chance] if player == B else [player_chance[k] for k in W_chance]
            first_choice = sum(first_choice, [])
            first_choice = list(set(sum(first_choice, [])))
            
            # second_choice:不走直接输
            second_choice = [opponent_chance[k] for k in B_chance] if player == W else [opponent_chance[k] for k in W_chance]
            second_choice = sum(second_choice, [])
            second_choice = list(set(sum(second_choice, [])))
            
            # third_choice:假如对方没有冲四活四等，那么自己的活三，走了也是直接赢
            third_choice = player_chance["活3"] if "活3" in player_chance else []
            third_choice = list(set(sum(third_choice, [])))

            return first_choice or second_choice or third_choice

        def win_chance_mul_lines():
            my_3 = sum(player_chance["活2"], [])
            my_4 = sum(player_chance["冲3"], [])
            your_live_3 = sum(opponent_chance["活3"], [])

            my_33 = [item[0] for item in Counter(my_3).items() if item[1] > 1]
            my_44 = [item[0] for item in Counter(my_4).items() if item[1] > 1]
            my_43 = [item for item in my_4 if item in my_3]

            if player == B:
                # 针对黑棋，自己的四三 > 对方的活三
                attack = [item for item in my_43 if item not in my_44 + my_33]
                if not attack and your_live_3:
                    attack = your_live_3 + my_4
                # todo: 43不能在同一行，比如 0 1 1 1 0 0 1 0 0，此时电脑会判断中间两个0能够组成43胜，但是其实是长连禁手
            else:
                # 针对白棋，自己四四或四三 > 对方的活三 > 自己的三三，都没有实际上返回的是 False
                if my_44 + my_43:
                    attack = my_44 + my_43
                else:
                    attack = your_live_3 + my_4 if your_live_3 else my_33
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
                    sec = your_33 + my_4 if your_33 else []
                else:
                    fir = [item for item in your_43 if item not in your_44 + your_33]
                    sec = []
                defence = fir if fir else sec
                ret = list(set(defence))
            return ret

        def normal_chance():
            # 从["冲3", "活2", "冲2", "冲1", "活1"]中选择
            temp = [i[j] for i in (player_chance, opponent_chance) for j in ("冲3", "活2")]
            temp = sum(temp, [])

            if self.settle:
            	# 解题时，只管进攻
            	ret = list(set(sum(temp, [])))
            else:
            	# 游戏时，还需要看更多情况
            	worst_line = [i[j] for i in (player_chance, opponent_chance) for j in ("冲2", "冲1", "活1")]
            	worst_pos = sum(sum(worst_line, []), [])
            	worst = [item[0] for item in sorted(Counter(worst_pos).items(), key=lambda x: x[1],reverse=True)][:5]
            	ret = list(set(sum(temp, []))) + worst
            return ret
            
            

        if self.winner:
            return False

        self.inside_make_line()
        self.win_announce(show=show)

        player = W if self.step % 2 else B
        opponent = W if player == B else B
        player_chance = self.values[player]
        opponent_chance = self.values[opponent]

        return win_chance_single_line() or win_chance_mul_lines() or normal_chance()

    def min_max_search(self, DEEPS=5, start=False, max_deep=0):
        def _logging(_pos, _deeps):
            if _deeps == DEEPS:
                logger.debug(f"The first step is {_pos}")

        def win_or_lose(deeps):
            if start and time() - start > max_deep:
                return 0
            global func_count
            func_count += 1
            if not self.winner:
                if deeps == 0:
                    my_score = sum([SCORE[key] * len(v) for (key, v) in self.values[player].items()])
                    your_score = sum([SCORE[key] * len(v) for (key, v) in self.values[opponent].items()])
                    return my_score - your_score
                else:
                    poss = self.analyse(show=False)
                    if not poss:
                        return False
                    result = [0] * len(poss)
                    next_player = B if (self.step + 1) % 2 == 1 else W
                    for ind, pos in enumerate(poss):
                        _logging(pos, deeps)
                        self.move(pos, show=False)
                        if deeps == DEEPS:
                            new_deeps = deeps - 1 if len(poss) > 1 else 0
                        else:
                            new_deeps = deeps if len(poss) == 1 else deeps - 1
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
                        if max(result) == 9999999:
                            step.append([self.step, poss[result.index(max(result))]])
                        else:
                            step.clear()
                        return max(result)
                    else:
                        if min(result) == 9999999:
                            step.append([self.step, poss[::-1]])
                        return min(result)
            elif self.winner == player:
                step.append([self.step, False])
                return 9999999
            else:
                return -9999999

        if self.winner:
            return False

        player = W if self.step % 2 else B
        opponent = W if player == B else B
        fin_result, fin_poss = win_or_lose(DEEPS)
        best_choice = fin_poss[fin_result.index(max(fin_result))]
        return best_choice, max(fin_result), fin_poss, fin_result

    @cost_count
    def iterative_deepening(self, max_deep, timing=False):
        global func_count
        func_count = 0
        if not timing:
            for d in range(1, max_deep + 1, 2):
                ret = self.min_max_search(DEEPS=d)
                if ret:
                    pos, fen, fin_poss, fin_result = ret
                    if fen == 9999999:
                        break
                else:
                    pos = False
        else:
            start = time()
            d = -1
            while 1:
                d += 2
                if time() - start > max_deep:
                    break
                ret = self.min_max_search(DEEPS=d, start=start, max_deep=max_deep)
                if ret:
                    pos, fen, fin_poss, fin_result = ret
                    if fen == 9999999:
                        break
                else:
                    pos = False
        if pos:
            logger.debug(f"result：{fin_result}")
            logger.debug(f"poss  ：{fin_poss}")
            logger.debug(f"best  ： {pos}")
            logger.info(f"MMS:count {func_count} times, best_score={fen}")
        return pos


def settling():
    g = Gomokuy(settle=True)
    g.parse(a)
    pos = g.iterative_deepening(5)


def roading():
    road_map = defaultdict(list)
    for k in step[::-1]:
        t = k[1] if k[1] else [False]
        road_map[k[0]].append(t)
    road_map[min(road_map.keys())] = road_map[min(road_map.keys())][0]
    print(step)
    print("\nROAD MAP:")
    print(road_map)
    for k, v in road_map.items():
        print(f"{k}\t{len(v)}\t{v}")
    

if __name__ == '__main__':
    settling()
    roading()

    # s = 15
    # while 1:
    #     pos = input("!!!!\n")
    #     pos = (int(str(pos)[0]),int(str(pos)[1]))
    #     if pos not in road_map[s] and pos != road_map[s]:
    #         print("WRONG")
    #         continue
    #     s += 1
    #     ind = road_map[s].index(pos)
    #     road_map[s+1] = road_map[s+1][ind]
