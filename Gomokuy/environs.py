#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from conf import a
from collections import defaultdict

self_lines = []   # self.lines
self_width = min(15, len(a))
ADR = {
    0: {
        "冲1": 0, "冲2": 2, "冲3": 2, "冲4": 1, "冲5": 0, "冲6": 0,
        "活1": 1, "活2": 2, "活3": 2, "活4": 1, "活5": 0, "活6": 0},
    1: {
        "冲1": 0, "冲2": 2, "冲3": 1, "冲4": 0, "冲5": 0, "冲6": 0,
        "活1": 1, "活2": 1, "活3": 1, "活4": 0, "活5": 0, "活6": 0},
    2: {
        "冲1": 0, "冲2": 1, "冲3": 0, "冲4": 0, "冲5": 0, "冲6": 0,
        "活1": 1, "活2": 0, "活3": 0, "活4": 0, "活5": 0, "活6": 0},
}


def get_diagonals():
    def get_starter():
        tmp1 = []
        tmp2 = []
        for i in range(self_width):
            tmp1.append([i, 0])
            tmp2.append([0, i])
        return tmp1, tmp2

    fir, sec = get_starter()
    diagonals = []

    for way in (True, False):
        for ind in range(len(fir)):
            new_pos = fir[ind] if way else sec[ind]
            temp = []
            while 1:
                temp.append((new_pos[0], new_pos[1]))
                new_pos[0] += 1
                new_pos[1] += 1 if way else -1
                if max(new_pos) >= self_width or min(new_pos) < 0:
                    break
            if len(temp) >= 5:
                diagonals.append(temp)
                if len(temp) < self_width:
                    if way:
                        temp2 = [(item[1], item[0]) for item in temp]
                    else:
                        temp2 = [(self_width - item[1] - 1, self_width - item[0] - 1) for item in temp]
                    diagonals.append(temp2)
    return diagonals


def chesses(line, self_lines, loc, cell):
    if cell == 0:
        if not line[0]:
            # 全新状态，计入一边的空
            line[1].append(loc)
        else:
            # 已经有子了，默认放另一边
            line[3].append(loc)
    elif cell == line[4]:
        # 遇到相同的子。
        if len(line[3]) >= 3:
            self_lines.append(line)
            l_tmp = line[3]
            line = [
                [loc],  # 0：棋子
                [l_tmp],  # 1：第一边空
                [],  # 2：中空
                [],  # 3：第二边空
                cell,  # 4：棋子颜色
            ]
        elif line[3]:
            line[2], line[3] = line[3], []
            line[0].append(loc)
        else:
            line[0].append(loc)

    elif not line[0]:
        # 遇到第一个子
        line[0].append(loc)
        line[4] = cell
    else:
        # 遇到对方的子，清算
        self_lines.append(line)
        line = [
            [loc],  # 0：棋子
            [],  # 1：第一边空
            [],  # 2：中空
            [],  # 3：第二边空
            cell,  # 4：棋子颜色
        ]
        # 一行看完，清算
    return line, self_lines


def new_linear(sid, row):
    global self_lines
    ret = [
        [],  # 0：棋子
        [],  # 1：第一边空
        [],  # 2：中空
        [],  # 3：第二边空
        False,  # 4：棋子颜色
    ]
    for col in range(self_width):
        loc = (row, col) if sid else (col, row)
        cell = a[row][col] if sid else a[col][row]
        ret, self_lines = chesses(ret, self_lines, loc, cell)

    # 一行看完，清算
    self_lines.append(ret)


if __name__ == '__main__':

    def inside_line_grouping(line, chess, self_values):
        t = len(line[0])
        t = 6 if t >= 6 else t
        if line[1] and line[3]:
            key = "活" + str(t) if t + len(line[2]) <= 4 else "冲" + str(t)
        elif line[1] or line[2] or line[3]:
            if t == 1:
                return self_values
            key = "冲" + str(t)
        else:
            return self_values
        sli = ADR[len(line[2])][key]
        line[1] = line[1][:sli]
        line[3] = line[3][:sli]
        format_line = line[1] + line[2] + line[3]
        self_values[chess][key].append(format_line)
        return self_values

    for sid in (True, False):
        for row in range(self_width):
            new_linear(sid, row)

    for line in get_diagonals():
        ret = [
            [],  # 0：棋子
            [],  # 1：第一边空
            [],  # 2：中空
            [],  # 3：第二边空
            False,  # 4：棋子颜色
        ]
        for pos in line:
            loc = pos
            cell = a[loc[0]][loc[1]]
            ret, self_lines = chesses(ret, self_lines, loc, cell)

        self_lines.append(ret)

    final = []
    for line in self_lines:
        if not line[0]:
            continue
        if sum([len(i) for i in line[:4]]) < 5:
            continue
        space = line[1] + line[2] + line[3]
        if not space:
            continue
        line[1].reverse()
        final.append(line)
    values = {
            1: defaultdict(list),
            2: defaultdict(list)}
    for line in final:
        inside_line_grouping(line, line[4], values)
    print(values)

