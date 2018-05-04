#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
from base import BlackWhite, B, W, timing, show_timing, PRINTING
import numpy as np
from casing import *


logger = logging.getLogger('Gomoku')
jmp = [0, 0]
WIN = 9999999
LOSE = -9999999


class Gomokuy(BlackWhite):
    def __init__(self, forbidden=True):
        BlackWhite.__init__(self, forbidden=forbidden)
        self.player = 2

    def probe(self, loc, show=True):
        ret = BlackWhite.move(self, loc, show=show)
        if not ret:
            print(f"self.winner = {self.winner}")
            self.show_situation()
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

    def min_max(self, max_deep=5):
        def alpha_beta(deep, v_max, v_min):
            def deeper():
                flag = False

                self.probe(pos, show=False)

                if self.winner == 2:
                    situation = alpha_beta(new_deeps, v_max, v_min)
                elif self.winner == self.player:
                    situation = WIN
                    flag = True
                else:
                    # 这时候几乎一定是白棋走的，假如是禁手可能是黑棋
                    situation = LOSE
                    if next_player != self.player:
                        # 因为对方落子失利 -> flag = True，因为自己禁手失利 pass
                        flag = True

                self.undo()
                return flag, situation

            if deep == max_deep:
                return self.get_score()
            else:
                next_player = W if self.step % 2 else B

                if self.forced and next_player == self.player:
                    # 被对方用冲四逼着走时，不计入步数，但是己方是没必要用冲四拖延时间的。
                    new_deeps = deep - 1
                else:
                    new_deeps = deep + 1

                result = [0] * len(self.candidates)
                for ind, pos in enumerate(self.candidates):
                    done, temp_score = deeper()

                    result[ind] = temp_score
                    if done:
                        self.translation_table[self.zob_key]["candidates"] = [pos]

                    if next_player == self.player:
                        if temp_score == WIN:
                            jmp[1] += 1
                            break
                    else:
                        if temp_score == LOSE:
                            jmp[1] += 1
                            break

                if deep == 0:
                    return result
                elif next_player == self.player:
                    return max(result)
                else:
                    return min(result)

        fin_result = alpha_beta(0, LOSE, WIN)
        best_choice = self.candidates[fin_result.index(max(fin_result))]

        return best_choice, max(fin_result), self.candidates, fin_result

    @timing
    def iterative_deepening(self, max_deep):
        self.player = W if self.step % 2 else B

        if self.forced:
            return self.candidates[0]

        for d in range(1, max_deep + 1, 2):
            logger.debug(f"迭代深度：{d}")

            pos, fen, fin_poss, fin_result = self.old_min_max(max_deep=d)

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

    g = Gomokuy()
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
        g = Gomokuy()
        g.load(ending)
        res = g.iterative_deepening(5)
        passing = "通过" if res == ans[idx] else "未通过"
        time_cost = int((time.time() - time_start) * 1000)

        logger.info(f"第{ind_str}题：{passing}\t耗时: {time_cost} ms")


if __name__ == '__main__':
    settling(case[1])
    # test_case()
