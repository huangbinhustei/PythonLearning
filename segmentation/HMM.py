import frequency

import os
wen_dang = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))  + "/DATA/doclist_mini.txt"
# wen_dang = "/Users/baidu/微云/project/segmentation/testdata/gamelistsmall.txt"
out_put_list = []


def the_long_the_better(leader):
    for_next = frequency.find_next
    if for_next(wen_dang, leader[0], top=1):
        sec = for_next(wen_dang, leader[0], top=1)[0]  # 返回的是二维数组，因为只用top1这里直接脱掉一层
        if sec[1] / leader[1] > 0.7:
            # new_leader = list(leader[0]+sec[0],sec[1])
            temp_str1 = leader[0] + sec[0]
            new_leader = [temp_str1, sec[1]]
            the_long_the_better(new_leader)
        elif len(leader[0]) > 2:
            # print(leader[0])
            out_put(leader[0])
    return


def out_put(temp):
    # out_put_list.append(four_out_put)
    for i in range(len(out_put_list)):
        if out_put_list[i].count(temp) != 0:
            return
        if temp.count(out_put_list[i]) != 0:
            out_put_list[i] = temp
            return
    out_put_list.append(temp)


# 下面才是真正的入口


topx = frequency.top(wen_dang, top=1500)
for me_item in topx:
    the_long_the_better(me_item)
print(out_put_list)



