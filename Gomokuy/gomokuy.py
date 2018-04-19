#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
from base import BlackWhite, B, W, timing, show_timing, PRINTING
from conf import *

# v_max = -9999999
# v_min = 9999999
ROADS = {0: (0, 1), 1: (1, 0), 2: (1, 1), 3: (1, -1)}
logger = logging.getLogger('Gomoku')
logger.setLevel(logging.INFO)
jmp = [0, 0]
WIN = 9999999
LOSE = -9999999


start = 12
steps = []
test = set([])


class Gomokuy(BlackWhite):
    def __init__(self, forbidden=True):
        BlackWhite.__init__(self, forbidden=forbidden)
        self.player = 2

    def min_max(self, max_deep=5):
        def alpha_beta(deep, v_max, v_min):
            if deep == max_deep:
                steps.append([self.records[start:], "No"])
                return self.situation
            else:
                next_player = B if (self.step + 1) % 2 == 1 else W
                poss = self.candidates
                result = [0] * len(poss)

                if self.forced and next_player == self.player:
                    # 被对方用冲四逼着走时，不计入步数，但是己方是没必要用冲四拖延时间的。
                    new_deeps = deep - 1
                else:
                    new_deeps = deep + 1

                for ind, pos in enumerate(poss):
                    ret = self.move(pos, show=False)
                    if not ret:
                        print(f"{pos}落子失败！{self.records}")
                        raise TypeError
                    if self.winner == 2:
                        temp_score = alpha_beta(new_deeps, v_max, v_min)
                    elif self.winner == player:
                        steps.append([self.records[start:], "Win"])
                        temp_score = WIN

                        self.translation_table[self.zob_key] = {
                            "pos": pos,
                            "result": WIN,
                        }
                        self.set_zob()
                    else:
                        steps.append([self.records[start:], "Lose"])
                        temp_score = LOSE

                        self.translation_table[self.zob_key] = {
                            "pos": pos,
                            "result": LOSE,
                        }
                        self.set_zob()

                    self.undo()
                    result[ind] = temp_score

                    if next_player != player:
                        if temp_score <= v_max:
                            jmp[1] += 1
                            break
                        # else:
                        #     v_max = temp_score
                    else:
                        if temp_score >= v_min:
                            jmp[1] += 1
                            break
                        # else:
                        #     v_min = temp_score

                if deep == 0:
                    return result, poss
                else:
                    ret_result = max(result) if next_player == player else min(result)
                    return ret_result

        if self.winner != 2:
            return False

        player = W if self.step % 2 else B
        fin_result, fin_poss = alpha_beta(0, LOSE, WIN)
        best_choice = fin_poss[fin_result.index(max(fin_result))]
        return best_choice, max(fin_result), fin_poss, fin_result

    @timing
    def iterative_deepening(self, max_deep):
        self.player = W if self.step % 2 else B

        if self.forced:
            return self.candidates[0]

        pos = False
        for d in range(1, max_deep + 1, 2):
            logger.debug(f"迭代深度：{d}")
            ret = self.min_max(max_deep=d)
            if not ret:
                continue
            pos, fen, fin_poss, fin_result = ret
            if fen == 9999999:
                logger.info(f"break in iterative_deepening @ deep = {d}")
                break

        if pos:
            logger.info("result：{}".format(fin_result))
            logger.info("poss  ：{}".format(fin_poss))
            logger.info("best  ： {0} when step is {1}".format(pos, self.step))

        return pos


def settling(ending):
    logger.setLevel(logging.DEBUG)

    logger.info("开始解题")

    g = Gomokuy()
    g.load(table=ending)
    global start
    start = g.step
    g.show_situation()
    result = g.iterative_deepening(5)
    logger.info(f"置换表长度：{len(g.translation_table.keys())}")

    show_timing()
    print(jmp)

    # global steps
    # for l in steps:
    #     if l[0][0] == (3, 8):
    #         print(l)

    return result


def test_case():
    logger.setLevel(logging.ERROR)
    case = {
        "name": [one, two, three, four, five, six, seven, eight, nine, ten, eleven],
        "result": [(2, 6), (3, 5), (6, 6), (4, 7), (7, 4), (3, 8), (5, 7), (5, 8), (7, 8), (7, 9), (5, 5)]
    }
    result = []

    for idx, ending in enumerate(case["name"]):
        print(f"正在解题，当前第{idx+1}题")
        g = Gomokuy()
        g.load(ending)
        time_start = time.time()
        res = g.iterative_deepening(5)
        time_cost = int((time.time() - time_start) * 1000)
        result.append([res == case["result"][idx], time_cost])
    for ind, line in enumerate(result):
        if ind < 9:
            print(f"第 {ind+1}题：{line}")
        else:
            print(f"第{ind+1}题：{line}")


if __name__ == '__main__':
    # settling(three)
    test_case()
    _a = input()

