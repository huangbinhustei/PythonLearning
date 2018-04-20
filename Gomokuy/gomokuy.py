#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
from base import BlackWhite, B, W, timing, show_timing, PRINTING
from conf import *
from casing import *

# v_max = -9999999
# v_min = 9999999

logger = logging.getLogger('Gomoku')
logger.setLevel(logging.INFO)
jmp = [0, 0]
WIN = 9999999
LOSE = -9999999


class Gomokuy(BlackWhite):
    def __init__(self, forbidden=True):
        BlackWhite.__init__(self, forbidden=forbidden)
        self.player = 2

    def min_max(self, max_deep=5):
        def alpha_beta(deep, v_max, v_min):
            if deep == max_deep:
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
                        logger.error(f"{pos}落子失败！{self.records}")
                        raise RuntimeError
                    if self.winner == 2:
                        temp_score = alpha_beta(new_deeps, v_max, v_min)
                    elif self.winner == player:
                        temp_score = WIN

                        self.set_zob()
                        self.translation_table[self.zob_key]["pos"] = pos
                        self.translation_table[self.zob_key]["result"] = WIN
                        
                    else:
                        temp_score = LOSE

                        self.set_zob()
                        self.translation_table[self.zob_key]["pos"] = pos
                        self.translation_table[self.zob_key]["result"] = LOSE                        

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
                logger.debug(f"break in iterative_deepening @ deep = {d}")
                break

        if pos:
            logger.debug("result：{}".format(fin_result))
            logger.debug("poss  ：{}".format(fin_poss))
            logger.debug("best  ： {0} when step is {1}".format(pos, self.step))

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
    
    _a = input()
    logger.info("任务完成，点击回车键退出")
    
    return result


def test_case():
    logger.setLevel(logging.INFO)

    result = []

    logger.info("开始解题")
    for idx, ending in enumerate(case):
        ind_str = " " + str(idx+1) if idx < 9 else str(idx+1)
        
        g = Gomokuy()
        g.load(ending)

        time_start = time.time()
        res = g.iterative_deepening(5)
        time_cost = int((time.time() - time_start) * 1000)

        passing = "通过" if res == ans[idx] else "未通过"

        logger.info(f"第{ind_str}题：{passing}\t耗时: {time_cost} ms")


if __name__ == '__main__':
    # settling(case[14])
    test_case()
