import os
import frequency
from datetime import datetime

start = datetime.now()
wen_dang = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/doclist_all.txt"
# wen_dang = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/DATA/words.txt"
out_put_list = []
threshold = 0.8
for_next = frequency.find_next


def out_put(temp):
    for i in range(len(out_put_list)):
        if out_put_list[i].count(temp) != 0:
            return
        if temp.count(out_put_list[i]) != 0:
            out_put_list[i] = temp
            return
    out_put_list.append(temp)


def the_long_the_better(leader, this_bool):
    # 会匹配两次，假如this_bool = False 表示先向后加字，加满了之后再在词前面加字，加满了之后再输出。假如=True就是反过来
    # 先向前，再向后（用True），准确率要高一些。
    temp = for_next(wen_dang, leader[0], medal2=3, reverse=this_bool)
    if temp:
        if not this_bool:
            sec = temp[0]  # 返回的是二维数组，因为只用top1这里直接脱掉一层
            if (sec[1] - 1) / leader[1] > threshold:
                new_leader = [leader[0] + sec[0], sec[1]]
                the_long_the_better(new_leader, this_bool)
            elif len(leader[0]) > 2:
                the_long_the_better(leader, not this_bool)  # 一个方向匹配完之后，反方向再来一次
        else:
            front = temp[0]
            if (front[1] - 1) / leader[1] > threshold:
                new_front = [front[0] + leader[0], front[1]]
                the_long_the_better(new_front, not this_bool)
            elif len(leader[0]) > 2:
                out_put(leader[0])
                return leader[0]


# 下面才是真正的入口


with open(wen_dang, 'r', encoding='utf-8') as f:
# with open(wen_dang, 'r', encoding='gbk') as f:
    target_words = f.readlines()
    need_pop = " "

    def me_replace(str11):
        return "".join(str11.split(need_pop))
    topx = frequency.top(target_words, medal=int(1/threshold))
    for me_item in topx:
        need_pop = the_long_the_better(me_item, True)
    if need_pop:
        target_words = list(map(me_replace, target_words))
    print(datetime.now() - start)
    print(out_put_list)


# topx = frequency.top(wen_dang, "", medal=int(1 / threshold))
# print(datetime.now() - start)
# for me_item in topx:
#     the_long_the_better(me_item, False)
#
# print(out_put_list)
