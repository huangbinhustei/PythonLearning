# -*- coding: utf-8 -*-

data_grid = [
    [0, 2, 0, 0],
    [0, 2, 2, 4],
    [0, 4, 4, 8],
    [0, 4, 2, 16]
]


def refresh(data):
    for item in data:
        print (item)


def new_grid(data):
    for line in data_grid:
        for item in line:
            pass


def vertical(up=True):
    '''

    :param up:
     up = True :向上移动,反之向下移动
     首先遍历列,然后反向合并列
    :return:
    '''

    for cal in range(4):
        new_cal = [0, 0, 0, 0]

        if up:
            i = 0
            step = 1
            for row in range(4):
                if data_grid[row][cal] == 0:
                    continue
                elif new_cal[i] == 0:
                    new_cal[i] = data_grid[row][cal]
                elif new_cal[i] == data_grid[row][cal]:
                    new_cal[i] *= 2
                    i += step
                else:
                    i += step
                    new_cal[i] = data_grid[row][cal]
        else:
            i = 3
            step = -1
            for row in range(4):
                row = 3-row
                if data_grid[row][cal] == 0:
                    continue
                elif new_cal[i] == 0:
                    new_cal[i] = data_grid[row][cal]
                elif new_cal[i] == data_grid[row][cal]:
                    new_cal[i] *= 2
                    i += step
                else:
                    i += step
                    new_cal[i] = data_grid[row][cal]
        for row in range(4):
            data_grid[row][cal] = new_cal[row]


def horizontal(left=True):
    for row in range(4):
        new_row = [0, 0, 0, 0]

        if left:
            i = 0
            step = 1
            for cal in range(4):
                if data_grid[row][cal] == 0:
                    continue
                elif new_row[i] == 0:
                    new_row[i] = data_grid[row][cal]
                elif new_row[i] == data_grid[row][cal]:
                    new_row[i] *= 2
                    i += step
                else:
                    i += step
                    new_row[i] = data_grid[row][cal]
        else:
            i = 3
            step = -1
            for cal in range(4):
                cal = 3 - cal
                if data_grid[row][cal] == 0:
                    continue
                elif new_row[i] == 0:
                    new_row[i] = data_grid[row][cal]
                elif new_row[i] == data_grid[row][cal]:
                    new_row[i] *= 2
                    i += step
                else:
                    i += step
                    new_row[i] = data_grid[row][cal]
        for cal in range(4):
            data_grid[row][cal] = new_row[cal]


if __name__ == '__main__':
    refresh(data_grid)
    while 1:
        x = input("方向")
        if x == "1":
            vertical(True)
        elif x == "2":
            vertical(False)
        elif x == "3":
            horizontal(True)
        elif x == "4":
            horizontal(False)
        else:
            break
        refresh(data_grid)


