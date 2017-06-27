from functools import wraps
import time


ROADS = {0: (0, 1), 1: (1, 0), 2: (1, 1), 3: (1, -1)}
a = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 0
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 1
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 2
    [0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 0, 0],   # 3
    [0, 0, 0, 0, 2, 0, 2, 0, 0, 0, 0, 0],   # 4
    [0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0],   # 5
    [0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 0],   # 6
    [0, 0, 0, 1, 2, 0, 0, 0, 2, 0, 0, 0],   # 7
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 8
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 9
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 10
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]   # 11
#    0  1  2  3  4  5  6  7  8  9  10 11

a4 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 0
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 1
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],   # 2
    [0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0],   # 3
    [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],   # 4
    [0, 0, 0, 0, 2, 1, 2, 2, 1, 0, 0, 0],   # 5
    [0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0],   # 6
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 7
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 8
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 9
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 10
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]   # 11
#    0  1  2  3  4  5  6  7  8  9  10 11

aa = [
    # 这里的胜负判断有问题，假如黑棋走（7，3），那么是长连禁手负，或者说是四三三禁手负
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 0
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 1
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 2
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 3
    [0, 0, 0, 1, 0, 2, 0, 0, 2, 0, 0, 0],   # 4
    [0, 0, 0, 0, 2, 0, 2, 1, 2, 0, 0, 0],   # 5
    [0, 0, 0, 1, 2, 1, 1, 0, 0, 0, 0, 0],   # 6
    [0, 0, 0, 0, 1, 1, 1, 2, 2, 0, 0, 0],   # 7
    [0, 0, 0, 0, 2, 2, 1, 1, 2, 0, 0, 0],   # 8
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],   # 9
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 10
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]   # 11
#    0  1  2  3  4  5  6  7  8  9  10 11

SCORE = {
    "活4": 100000,
    "冲4": 10000,
    "活3": 1000,
    "冲3": 100,
    "活2": 10,
    "冲2": 1,
    "活1": 1,
    "冲1": 1,
}


def cost_count(func):
    @wraps(func)
    def costing(*args, **kw):
        a = time.time()
        ret = func(*args, **kw)
        time_cost = int((time.time()-a) * 1000)
        if time_cost > 0:
            print("Func(" + str(func.__name__) + ")\tcost: " + str(time_cost) + " ms")
        else:
            time_cost = int((time.time()-a) * 1000000)
            print("Func(" + str(func.__name__) + ")\tcost: " + str(time_cost) + " μs")
        return ret
    return costing
