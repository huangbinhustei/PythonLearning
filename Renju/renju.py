#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
from base import BlackWhite, B, W, timing, show_timing
import numpy as np
from casing import *


logger = logging.getLogger('Renju')
jmp = [0, 0]
WIN = 9999999
LOSE = -9999999


class Renjuy(BlackWhite):
    def __init__(self, forbidden=True):
        BlackWhite.__init__(self, forbidden=forbidden)
        self.player = 2

    def probe(self, loc, show=True):
        ret = BlackWhite.move(self, loc, show=show)
        if not ret:
            self.show_situation()
            logger.error(f"self.winner = {self.winner}")
            logger.error(f"{loc}落子失败！{self.records}")
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
                    # if situation == WIN:
                    #     self.translation_table[self.zob_key]["candidates"] = [i]
                    if beta <= alpha:
                        jmp[0] += 1
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
                        jmp[0] += 1
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


def settling(ending):
    logger.setLevel(logging.DEBUG)

    logger.info("开始解题")

    g = Renjuy()
    g.load(table=ending)
    g.show_situation()
    result = g.iterative_deepening(5)
    logger.info(f"置换表长度：{len(g.translation_table.keys())}")

    show_timing()
    logger.info(jmp)
    
    _a = input("任务完成，点击回车键退出\n")
    
    return result


def test_case():
    logger.setLevel(logging.INFO)
    logger.info("开始解题")

    for idx, ending in enumerate(case):
        ind_str = " " + str(idx+1) if idx < 9 else str(idx+1)

        time_start = time.time()
        g = Renjuy()
        g.load(ending)
        res = g.iterative_deepening(5)
        passing = "通过" if res == ans[idx] else "未通过"
        time_cost = int((time.time() - time_start) * 1000)

        logger.info(f"第{ind_str}题：{passing}\t耗时: {time_cost} ms")


if __name__ == '__main__':
    # settling(case[1])
    test_case()
