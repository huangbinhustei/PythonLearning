#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from base import BlackWhite, B, W, timing, show_timing, PRINTING
from conf import a

# v_max = -9999999
# v_min = 9999999
ROADS = {0: (0, 1), 1: (1, 0), 2: (1, 1), 3: (1, -1)}
logger = logging.getLogger('Gomoku')
logger.setLevel(logging.INFO)
jmp = [0, 0]


class Gomokuy(BlackWhite):
    def __init__(self, forbidden=True, examinee=2):
        BlackWhite.__init__(self, forbidden=forbidden, examinee=examinee)

    @timing
    def get_candidates(self, deep):
        zob = self.get_zob()
        if not zob:
            return self.candidates
        elif zob["result"] == 9999999:
            # 可以直接用之前的最佳结果
            jmp[0] += 1
            return [zob["pos"]]
        else:
            return self.candidates

    @timing
    def min_max(self, max_deep=5):

        def alpha_beta(deep, v_max, v_min):
            if deep == max_deep:
                return self.situation
            else:
                next_player = B if (self.step + 1) % 2 == 1 else W

                # ------------规避从 zob 中取出已经的位置已经有子的尝试 begin -----------------
                zob = self.get_zob()
                if not zob:
                    poss = self.candidates
                elif zob["result"] == 9999999:
                    # 可以直接用之前的最佳结果
                    jmp[0] += 1
                    return 9999999
                else:
                    poss = self.candidates
                # poss = self.get_candidates(max_deep - deep)

                # ------------规避从 zob 中取出已经的位置已经有子的尝试 end -------------------

                if not poss:
                    if self.examinee != 2:
                        # 解题时假如 poss 为空，就算解题失败
                        return -9999999
                    else:
                        return False
                result = [0] * len(poss)
                if deep == 0 and len(poss) == 1:
                    new_deeps = max_deep
                else:
                    new_deeps = deep + 1
                for ind, pos in enumerate(poss):
                    ret = self.move(pos, show=False)
                    if not ret:
                        print(f"{pos}落子失败！")
                        raise TypeError
                    if self.winner == 2:
                        temp_score = alpha_beta(new_deeps, v_max, v_min)
                    elif self.winner == player:
                        temp_score = 9999999
                        self.translation_table[self.zob_key] = {
                            "pos": pos,
                            "result": 9999999,
                            "record": self.records,
                        }
                    else:
                        temp_score = -9999999
                        self.translation_table[self.zob_key] = {
                            "pos": pos,
                            "result": -9999999,
                            "record": self.records,
                        }

                    self.undo()
                    result[ind] = temp_score

                    if temp_score >= 9999999 and next_player == player:
                        v_max = temp_score
                        jmp[1] += 1
                        break
                    elif temp_score <= -9999999 and next_player != player:
                        v_min = temp_score
                        jmp[1] += 1
                        break
                if deep == 0:
                    return result, poss
                else:
                    ret_result = max(result) if next_player == player else min(result)
                    return ret_result

        if self.winner != 2:
            return False

        player = W if self.step % 2 else B
        fin_result, fin_poss = alpha_beta(0, -9999999, 9999999)
        best_choice = fin_poss[fin_result.index(max(fin_result))]
        return best_choice, max(fin_result), fin_poss, fin_result

    @timing
    def iterative_deepening(self, max_deep):
        pos = False
        for d in range(1, max_deep + 1, 2):
            # logger.debug(f"迭代深度：{d}")
            print(f"迭代深度：{d}")
            ret = self.min_max(max_deep=d)
            if not ret:
                continue
            pos, fen, fin_poss, fin_result = ret
            if fen == 9999999:
                print(f"break in iterative_deepening @ deep = {d}")
                break

        if pos:
            logger.info("result：{}".format(fin_result))
            logger.info("poss  ：{}".format(fin_poss))
            logger.info("best  ： {0} when step is {1}".format(pos, self.step))
        return pos


def settling():
    g = Gomokuy()
    g.load(table=a)
    g.examinee = B if g.step % 2 == 0 else W
    print(f"g.examinee = {PRINTING[g.examinee]}")
    g.show_situation()
    g.iterative_deepening(7)
    print(f"+++ {len(g.translation_table.keys())} +++")


if __name__ == '__main__':
    settling()
    show_timing()
    print(jmp)
