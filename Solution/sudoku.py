from collections import defaultdict
import time
import copy


grid1 = [
    [2,0,4,0,0,6,0,0,5],
    [0,0,3,5,0,0,9,2,0],
    [0,0,5,0,4,0,8,0,7],
    [5,0,0,0,2,8,6,7,3],
    [3,2,7,0,0,0,0,0,0],
    [4,6,0,7,0,1,2,0,0],
    [1,0,2,0,6,0,0,0,0],
    [0,0,9,0,8,2,0,0,0],
    [8,0,6,9,0,5,1,4,0]]


grid2 = [
    [5,8,4,6,2,7,0,0,0],
    [0,0,0,9,0,0,0,0,0],
    [9,0,7,0,0,0,0,0,6],
    [0,0,0,0,3,0,0,0,0],
    [8,0,6,0,5,0,0,4,0],
    [0,4,0,7,0,9,0,0,1],
    [0,0,8,0,0,0,0,3,0],
    [1,6,0,3,0,0,2,0,7],
    [0,2,5,8,0,1,0,6,4]]


grid3 = [
    [0,0,0,5,1,9,3,8,0],
    [6,0,0,0,0,3,0,0,5],
    [0,0,0,0,0,0,0,4,0],
    [0,4,0,0,0,0,0,9,8],
    [1,7,0,0,0,2,0,0,0],
    [0,0,5,0,4,0,0,0,0],
    [0,0,0,0,6,0,0,0,4],
    [8,0,0,0,0,0,2,0,0],
    [0,0,0,0,0,4,0,5,1],]


grid4 = [
    [0,0,0,0,0,7,6,0,4],
    [0,3,0,0,6,0,9,0,0],
    [0,0,0,0,0,0,0,0,5],
    [0,6,4,5,0,0,7,0,9],
    [0,0,2,6,7,0,0,0,0],
    [0,7,0,9,2,0,0,6,0],
    [0,9,1,0,0,0,0,3,0],
    [0,0,6,0,9,0,0,0,8],
    [8,2,0,0,0,0,0,0,7]]


grid5 = [
    [1,0,0,0,0,0,0,2,6],
    [0,7,0,8,0,0,0,5,0],
    [0,0,0,6,0,4,8,0,0],
    [0,0,0,0,0,0,9,7,0],
    [0,5,7,9,0,0,0,1,0],
    [0,0,0,0,3,0,0,0,5],
    [0,1,0,3,0,0,0,0,0],
    [3,0,0,0,0,0,0,6,7],
    [0,9,0,4,0,6,0,0,8]]


grid6 = [
    [0,0,5,3,0,0,0,0,0],
    [8,0,0,0,0,0,0,2,0],
    [0,7,0,0,1,0,5,0,0],
    [4,0,0,0,0,5,3,0,0],
    [0,1,0,0,7,0,0,0,6],
    [0,0,3,2,0,0,0,8,0],
    [0,6,0,5,0,0,0,0,9],
    [0,0,4,0,0,0,0,3,0],
    [0,0,0,0,0,9,7,0,0],]


class SUDOKU:
    def __init__(self):
        self.protal = []
        self.blank = 81
        self.solutions = []
        self.nine = defaultdict(list)

        self.dict_count = 0

        self.grid = []
        self.candidates = []
        for row in range(9):
            line_candidates = []
            line_grid = []
            for col in range(9):
                line_grid.append(0)
                line_candidates.append([1,2,3,4,5,6,7,8,9])
            self.candidates.append(line_candidates)
            self.grid.append(line_grid)

    def winning(self):
        tmp = []
        for line in self.grid:
            tmp.append(''.join([str(i) for i in line]))
        self.solutions.append(tmp)

    def checkout(self, row, col, shu):
        if self.grid[row][col]:
            return shu == self.grid[row][col]
        
        for i in range(9):
            if self.grid[row][i] == shu or self.grid[i][col] == shu:
                return False

        for i in range(3):
            for j in range(3):
                if self.grid[row//3*3+i][col//3*3+j] == shu:
                    return False

        self.grid[row][col] = shu
        self.blank -= 1
        return True

    def undo(self, row, col):
        self.blank += 1
        self.grid[row][col] = 0

    def danger(self, row, col, shu):
        def pop(row, col, shu):
            if self.grid[row][col] == 0 and shu in self.candidates[row][col]:
                self.candidates[row][col].remove(shu)
                if len(self.candidates[row][col]) == 1:
                    # 假如排除不可能数字之后，一个位置仅可能是一个数字
                    self.move(row, col, self.candidates[row][col][0])
        
        for i in range(9):
            pop(row, i, shu)
            pop(i, col, shu)

        for i in range(3):
            for j in range(3):
                pop(row//3 * 3 + i, col //3 * 3 + j, shu)

    def move(self, row, col, shu):
        ret = self.checkout(row, col, shu)
        if not ret:
            print(f'落子失败{row, col, shu}, {self.grid[row][col]}')
            exit(1)
        self.danger(row, col, shu)
    
    def update(self, grid):
        self.__init__()
        for row, line in enumerate(grid):
            self.protal.append(''.join([str(i) for i in line]))
            for col, cell in enumerate(line):
                if cell:
                    self.move(row, col, cell)
        if not self.blank:
            self.winning()

    def solve_from_dict(self):
        # 每一行/列/小九宫都有且只有一个1~9
        def pick_from_nine():
            for k, v in self.nine.items():
                if len(v) != 1:
                    continue
                _i, _j = v[0]
                self.move(_i, _j, k)

        def rowing():
            for row in range(9):
                self.nine.clear()
                for col in range(9):
                    if 0 == self.grid[row][col]:
                        for maybe in self.candidates[row][col]:
                            self.nine[maybe].append([row, col])
                pick_from_nine()

        def coling():
            for col in range(9):
                self.nine.clear()
                for row in range(9):
                    if 0 == self.grid[row][col]:
                        for maybe in self.candidates[row][col]:
                            self.nine[maybe].append([row, col])
                pick_from_nine()

        def griding():
            for left in range(3):
                for top in range(3):
                    self.nine.clear()
                    for row in range(3):
                        for col in range(3):
                            if 0 == self.grid[left * 3 + row][top * 3 + col]:
                                for maybe in self.candidates[left * 3 + row][top * 3 + col]:
                                    self.nine[maybe].append([left * 3 + row, top * 3 + col])
                    pick_from_nine()

        while self.blank:
            self.dict_count += 1
            tmp = self.blank
            rowing()
            coling()
            griding()
            if not self.blank:
                self.winning()
                break
            if self.blank == tmp:
                break

    def cage(self):
        def mini_cage_griding(l, t):
            ret = defaultdict(list)
            for row in range(3):
                for col in range(3):
                    if 0 == self.grid[l*3+row][t*3+col]:
                        for maybe in self.candidates[l*3+row][t*3+col]:
                            ret[maybe].append([l*3+row, t*3+col])
            
            # 如果行相同，过滤行，如果列相同，过滤列
            for k, v in ret.items():
                rows = [i[0] for i in v]
                if len(set(rows)) == 1:
                    # 说明这个数只可能在这一行，而它又必须在九宫之中
                    cage_row = rows[0]
                    for _col in range(9):
                        if _col //3 != t and self.grid[cage_row][_col] == 0 and k in self.candidates[cage_row][_col]:
                            self.candidates[cage_row][_col].remove(k)
                            if len(self.candidates[cage_row][_col]) == 1:
                                self.move(cage_row, _col, self.candidates[cage_row][_col][0])

                
                cols = [i[1] for i in v]
                if len(set(cols)) == 1:
                    # 说明这个数只可能在这一列，而它又必须在九宫之中
                    cage_col = cols[0]
                    for _row in range(9):
                        if _row // 3 != l and self.grid[_row][cage_col] == 0 and k in self.candidates[_row][cage_col]:
                            self.candidates[_row][cage_col].remove(k)
                            if len(self.candidates[_row][cage_col]) == 1:
                                self.move(_row, cage_col, self.candidates[_row][cage_col][0])

        for left in range(3):
            for top in range(3):
                mini_cage_griding(left, top)

    def solving(self):
        self.solve_from_dict()
        if self.blank:
            self.cage()


class DFF(SUDOKU):
    def __init__(self):
        SUDOKU.__init__(self)
        self.search_count = 0

    def get_first_zero(self):
        # 找到第一个 0 点，仅在 self.blank ！= 0 的时候才被调用
        for row in range(9):
            for col in range(9):
                if self.grid[row][col] == 0:
                    return row, col

    def search(self, row, col, candidate):
        self.search_count += 1
        ret = self.checkout(row, col, candidate)
        if not ret:
            return False

        if self.blank == 0:
            return True
        
        r, c = self.get_first_zero()
        for candidate in self.candidates[r][c]:
            if self.search(r, c, candidate):
                self.winning()
        self.undo(row, col)
    
    def big_solving(self):
        if self.blank:
            r, c = self.get_first_zero()
            for candidate in self.candidates[r][c]:
                self.search(r, c, candidate)
        # for offset, l in enumerate(self.protal):
        #     print(l + ': ' + ', '.join([g[offset] for g in self.solutions]))



for ind, grid in enumerate([grid1, grid2, grid3, grid4, grid5, grid6]):
    start = time.time()

    s = DFF()
    s.update(grid)
    s.solving()
    s.big_solving()
    print(f'第{ind + 1}题：词典{s.dict_count}，搜索{s.search_count}，解{len(s.solutions)}组，耗时{(time.time() - start)* 1000:.2f}ms')


