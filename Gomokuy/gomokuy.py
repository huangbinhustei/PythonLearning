#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import Counter, defaultdict
import logging

from base import BaseGame, B, W, timing, cost_dict
from conf import a

v_max = -9999999
v_min = 9999999
step = []
ROADS = {0: (0, 1), 1: (1, 0), 2: (1, 1), 3: (1, -1)}
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

logger = logging.getLogger('Gomoku')


class Gomokuy(BaseGame):
    def __init__(self, settle=False, restricted=True):
        BaseGame.__init__(self, restricted=restricted)
        self.settle = settle

    @timing
    def evaluate(self):
        lc = self.records[-1]
        player = self.table[lc[0]][lc[1]]
        opponent = W if player == B else B
        values = {
            B: defaultdict(list),
            W: defaultdict(list)}

        my_score = sum([SCORE[key] * len(v1) for (key, v1) in self.values[player].items()])
        your_score = sum([SCORE[key] * len(v2) for (key, v2) in self.values[opponent].items()])
        
        for direction in range(4):
            line = self.base_linear(lc[0], lc[1], player, direction)
            values = self.inside_line_grouping(line, player, values=values)
        
        my_score += sum([SCORE[key] * len(v1) for (key, v1) in values[player].items()])
        your_score += sum([SCORE[key] * len(v2) for (key, v2) in values[opponent].items()])

        for key, v1 in self.values[player].items():
            del_v1 = [l for l in v1 if lc in l]
            my_score -= SCORE[key] * len(del_v1)

        for key, v1 in self.values[opponent].items():
            del_v1 = [l for l in v1 if lc in l]
            my_score -= SCORE[key] * len(del_v1)
        
        # print(f"得分：{my_score - your_score}")
        return my_score - your_score

    @timing
    def old_evaluate(self):
        self.inside_make_line()

        player = W if self.step % 2 else B
        opponent = W if player == B else B

        my_score = sum([SCORE[key] * len(v1) for (key, v1) in self.values[player].items()])
        your_score = sum([SCORE[key] * len(v2) for (key, v2) in self.values[opponent].items()])
        return my_score - your_score

    @timing
    def gen(self):
        @timing
        def win_chance_single_line():
            # 自己有冲四、活四 -> 对方的冲四、活四 -> 自己的活三
            black_key = [i for i in ["冲4", "活4"] if i in self.values[B]]
            white_key = [i for i in ["冲4", "活4", "冲5", "活5", "冲6", "活6"] if i in self.values[W]]

            # first_choice:走了直接赢
            first_choice = [player_chance[k] for k in black_key] if player == B else [player_chance[k] for k in
                                                                                      white_key]
            first_choice = sum(first_choice, [])
            first_choice = list(set(sum(first_choice, [])))

            # second_choice:不走直接输
            second_choice = [opponent_chance[k] for k in black_key] if player == W else [opponent_chance[k] for k in
                                                                                         white_key]
            second_choice = sum(second_choice, [])
            second_choice = list(set(sum(second_choice, [])))

            # third_choice:假如对方没有冲四活四等，那么自己的活三，走了也是直接赢
            third_choice = player_chance["活3"] if "活3" in player_chance else []
            third_choice = list(set(sum(third_choice, [])))

            return first_choice or second_choice or third_choice

        @timing
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

        @timing
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
                worst = [item[0] for item in sorted(Counter(worst_pos).items(), key=lambda x: x[1], reverse=True)][:5]
                ret = list(set(sum(temp, []))) + worst
            return ret

        self.inside_make_line()

        player = W if self.step % 2 else B
        opponent = W if player == B else B
        player_chance = self.values[player]
        opponent_chance = self.values[opponent]

        return win_chance_single_line() or win_chance_mul_lines() or normal_chance()

    @timing
    def min_max_search(self, max_deep=5):
        v_max = -9999999
        v_min = 9999999

        def alpha_beta(deep):
            global v_max
            global v_min
            if deep == max_deep:
                return self.evaluate()
            else:
                next_player = B if (self.step + 1) % 2 == 1 else W
                poss = self.gen()
                if not poss:
                    return False
                result = [0] * len(poss)
                if deep == 0 and len(poss) == 1:
                    new_deeps = max_deep
                else:
                    new_deeps = deep + 1
                for ind, pos in enumerate(poss):
                    self.move(pos, show=False)
                    if self.winner:
                        if self.winner == player:
                            step.append([self.step, False])
                            temp_score = 9999999
                        else:
                            temp_score = -9999999
                    else:
                        temp_score = alpha_beta(new_deeps)
                    self.undo()
                    result[ind] = temp_score

                    if temp_score >= v_max and next_player == player:
                        v_max = max(temp_score, v_max)
                        break
                    elif temp_score <= v_min and next_player != player:
                        v_min = min(temp_score, v_min)
                        break
                if deep == 0:
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

        if self.winner:
            return False

        player = W if self.step % 2 else B
        fin_result, fin_poss = alpha_beta(0)
        best_choice = fin_poss[fin_result.index(max(fin_result))]
        return best_choice, max(fin_result), fin_poss, fin_result

    @timing
    def iterative_deepening(self, max_deep):
        pos = False
        for d in range(1, max_deep + 1, 2):
            ret = self.min_max_search(max_deep=d)
            if not ret:
                continue
            pos, fen, fin_poss, fin_result = ret
            if fen == 9999999:
                break
        if pos:
            logger.debug(f"result：{fin_result}")
            logger.debug(f"poss  ：{fin_poss}")
            logger.info(f"best  ： {pos}, score={max(fin_result)}, step={self.step}")
        return pos


def settling():
    g = Gomokuy(settle=True, restricted=True)
    g.parse(a)
    g.iterative_deepening(7)


def show_timing():
    print("\nTiming\n+-%-24s-+-%-12s-+-%-8s-+" % ("-" * 24, "-" * 12, "-" * 8))
    print("| %-24s | %-12s | %-8s |" % ("func name", "times", "cost"))
    print("+-%-24s-+-%-12s-+-%-8s-+" % ("-" * 24, "-" * 12, "-" * 8))
    for k, v in cost_dict.items():
        print("| %-24s | %-12d | %-8s |" % (k, v[0], str(round(v[1], 3))))
        # print(f"{k}\t{v[0]}\t{round(v[1], 3)}")
    print("+-%-24s-+-%-12s-+-%-8s-+\n" % ("-" * 24, "-" * 12, "-" * 8))


def road_finding():
    road_map = defaultdict(list)
    for k1 in step[::-1]:
        t = k1[1] if k1[1] else [False]
        road_map[k1[0]].append(t)
    road_map[min(road_map.keys())] = road_map[min(road_map.keys())][0]
    print("\nROAD MAP:")
    print(road_map)
    for k1, v1 in road_map.items():
        print(f"{k1}\t{len(v1)}\t{v1}")


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    settling()
    show_timing()
    road_finding()
