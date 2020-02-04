grid = [
[1, 0, 0, 1, 1, 1, 1, 1, 1],
[1, 0, 0, 1, 0, 0, 0, 0, 1],
[1, 0, 0, 1, 1, 1, 1, 0, 1],
[1, 0, 0, 0, 0, 0, 1, 0, 1],
[1, 0, 1, 0, 0, 0, 1, 0, 1],
[1, 0, 1, 0, 0, 0, 1, 0, 1],
[1, 1, 1, 1, 1, 1, 1, 0, 1],
[0, 0, 1, 0, 0, 0, 0, 0, 1],
[0, 0, 1, 0, 1, 1, 0, 0, 1],
[0, 0, 1, 0, 0, 0, 0, 0, 1],
[1, 1, 1, 1, 1, 1, 0, 0, 1],
[0, 0, 1, 0, 0, 1, 0, 0, 1],
[0, 0, 1, 0, 0, 1, 0, 0, 1],
[0, 0, 1, 1, 1, 1, 0, 0, 1]
]


mrow = len(grid)
mcol = len(grid[0])
start = [0, 0]


class Floading:
    def __init__(self, grid, start=[0, 0], end=[-1, -1]):
        self.nrow = len(grid)
        self.ncol = len(grid[0])
        self.start = start
        self.end = end
        self.grid = grid
        self.l = []
        for line in grid:
            info = ''
            for cell in line:
                info += f'{cell:3.0f}'
            self.l.append(info)
        

    def deeper(self, row, col, shu):
        if 0 <= row < self.nrow and 0 <= col < self.ncol:
            if self.grid[row][col] == 0 or 1 < self.grid[row][col] <= shu:
                return
            self.grid[row][col] = shu
            if (row, col) == (self.nrow -1, self.ncol - 1):
                print(shu)
                return True
            print(shu)
            self.deeper(row + 1, col, shu + 1)
            self.deeper(row - 1, col, shu + 1)
            self.deeper(row, col + 1, shu + 1)
            self.deeper(row, col - 1, shu + 1)
    
    def solving(self):
        while self.grid[self.end[0]][self.end[1]] == 1:
            self.deeper(0, 0, 2)
        for i, line in enumerate(self.grid):
            info = self.l[i] + ' -> '
            for cell in line:
                info += f'{cell:3.0f}'
            print(info)


            
x = Floading(grid)
x.solving()



for line in grid:
    l = ''
    for cell in line:
        l += f'{cell:3.0f}'

def deeper(row, col, shu):
    if shu == 1:
        return
    if row < 0 or col < 0 or row > mrow - 1 or col > mcol - 1:
        return
    if grid[row][col] == 0 or grid[row][col] > shu:
        return
    grid[row][col] = shu
    deeper(row + 1, col, shu - 1)
    deeper(row - 1, col, shu - 1)
    deeper(row, col + 1, shu - 1)
    deeper(row, col - 1, shu - 1)


i = 1
while 1:
    i = i + 1
    deeper(0, 0, i)    
    if grid[mrow - 1][mcol - 1] == 2:
        break


for line in grid:
    l = ''
    for cell in line:
        l += f'{cell:5.0f}'
    print(l)

