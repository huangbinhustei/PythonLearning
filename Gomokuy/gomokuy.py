#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import Counter, defaultdict
import logging

from base import BaseGame, B, W, timing, show_timing
from conf import a

v_max = -9999999
v_min = 9999999
ROADS = {0: (0, 1), 1: (1, 0), 2: (1, 1), 3: (1, -1)}
SCORE = {
    "冲6": 100000,
    "冲5": 100000,
    "活4": 100000,
    "冲4": 1000,
    "活3": 1000,
    "冲3": 10,
    "活2": 10,
    "冲2": 1,
    "活1": 1,
    "冲1": 0,
    "禁手": -100,
}
logger = logging.getLogger('Gomoku')


class Gomokuy(BaseGame):
    def __init__(self, settle=False, restricted=True, manual=[]):
        BaseGame.__init__(self, restricted=restricted, manual=manual)
        self.settle = settle
        if self.settle:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

    def score_calc(self, values):
        ret = {
            B: 0,
            W: 0}
        if self.restricted:
            for sid, d in values.items():
                for key, v1 in d.items():
                    key = "禁手" if sid == B and key in ("冲5", "冲6") else key
                    ret[sid] += SCORE[key] * len(v1)
        else:
            for sid, d in values.items():
                ret[sid] = sum([SCORE[key] * len(v1) for (key, v1) in d.items()])
        return ret

    @timing
    def evaluate(self):
        lc = self.records[-1]
        player = self.table[lc[0]][lc[1]]
        opponent = W if player == B else B

        # 落子之前的得分
        s1 = self.score_calc(self.values)
        my_score = s1[player]
        your_score = s1[opponent]

        # 落子之后，己方新增的 line 分需要加上，对方受影响的线要加回来。
        values = {
            B: defaultdict(list),
            W: defaultdict(list)}
        for direction in range(4):
            # 计算自己新增的 line， 以及对方受影响的棋子（opt）
            line, opt = self.base_linear(lc[0], lc[1], player, direction, modify=True)
            values = self.inside_line_grouping(line, player, values=values)
            if opt:
                # 假如有对方的棋子受影响，对应的 line 需要重算
                opt_line = self.base_linear(opt[0], opt[1], opponent, direction)
                values = self.inside_line_grouping(opt_line, opponent, values=values)
        s2 = self.score_calc(values)
        my_score += s2[player]
        your_score += s2[opponent]

        # 落子之后，对方一些 line 被破坏了，上面落子时已经重算了，这里直接全部删掉
        for key, v1 in self.values[player].items():
            del_v1 = [l for l in v1 if lc in l]
            my_score -= SCORE[key] * len(del_v1)
        for key, v1 in self.values[opponent].items():
            del_v1 = [l for l in v1 if lc in l]
            your_score -= SCORE[key] * len(del_v1)

        return my_score - your_score

    @timing
    def gen(self, deep):
        # @timing
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

        # @timing
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

        # @timing
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

        pos = self.get_zod(deep)
        if pos:
            return pos

        self.inside_make_line()
        player = W if self.step % 2 else B
        opponent = W if player == B else B
        player_chance = self.values[player]
        opponent_chance = self.values[opponent]

        ret = win_chance_single_line() or win_chance_mul_lines() or normal_chance()

        return ret

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
                poss = self.gen(max_deep - deep)
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
                        temp_score = 9999999 if self.winner == player else -9999999
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
                    self.translation_table[self.zod_key] = {
                        "pos": poss[result.index(max(result))],
                        "result": max(result),
                        "deep": max_deep - deep,
                    }
                    return max(result)
                else:
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
            logger.info("result：{}".format(fin_result))
            logger.info("poss  ：{}".format(fin_poss))
            logger.info("best  ： {0} when step is {1}".format(pos, self.step))
        return pos


def settling():
    g = Gomokuy(settle=True, restricted=True, manual=a)
    g.iterative_deepening(7)


if __name__ == '__main__':
    settling()
    show_timing()
