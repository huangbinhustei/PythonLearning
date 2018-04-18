#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

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
            print(f"迭代深度：{d}")
            ret = self.min_max(max_deep=d)
            if not ret:
                continue
            pos, fen, fin_poss, fin_result = ret
            if fen == 9999999:
                print(f"break in iterative_deepening @ deep = {d}")
                break

        global steps
        for i in steps:
            if i[0][0] == (6, 4):
                print(i)

        if pos:
            logger.info("result：{}".format(fin_result))
            logger.info("poss  ：{}".format(fin_poss))
            logger.info("best  ： {0} when step is {1}".format(pos, self.step))

        return pos


def settling():
    g = Gomokuy()
    g.load(table=eleven)
    global start
    start = g.step
    g.show_situation()
    # g.iterative_deepening(5)

    g.move((5, 5))
    g.move((5, 7))
    g.move((3, 7))
    g.move((2, 8))
    g.move((2, 6))
    g.show_situation()
    print(f"置换表长度：{len(g.translation_table.keys())}")


if __name__ == '__main__':
    settling()
    show_timing()
    print(jmp)
    _a = input()
