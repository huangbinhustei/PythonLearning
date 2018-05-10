@timing
def old_gen(self):
    def finder():
        fir = list(zip(*np.where(chance_of_mine[:, :] >= 8)))
        if fir:
            return fir
        elif list(zip(*np.where(chance_of_your[:, :] >= 8))):
            self.forced = True
            return list(zip(*np.where(chance_of_your[:, :] >= 8)))
        elif list(zip(*np.where(chance_of_mine[:, :] >= 6))):
            return list(zip(*np.where(chance_of_mine[:, :] >= 6)))
        elif list(zip(*np.where(chance_of_mine[:, :] >= 4))) + list(zip(*np.where(chance_of_your[:, :] >= 5))):
            return list(zip(*np.where(chance_of_mine[:, :] >= 4))) + list(zip(*np.where(chance_of_your[:, :] >= 5)))
        elif list(zip(*np.where(chance_of_mine[:, :] >= 2))) + list(zip(*np.where(chance_of_your[:, :] >= 4))):
            return list(zip(*np.where(chance_of_mine[:, :] >= 2))) + list(zip(*np.where(chance_of_your[:, :] >= 4)))
        else:
            return list(zip(*np.where(chance_of_mine[:, :] >= 1))) + list(zip(*np.where(chance_of_your[:, :] >= 1)))


    self.forced = False
    next_player = B if self.step % 2 == 0 else W
    opt_player = B if next_player == W else W
    chance_of_mine = self.score[:, :, next_player]
    chance_of_your = self.score[:, :, opt_player]

    self.candidates = finder()


@timing
def old_situation_updater(self, row, col, show=True):
    def get_offset_by_block(fir, sec, sd):
        def siding(side_location):
            # 用于判断边上是否堵住了，仅用于 line_ordering 函数
            # 返回 True 表示没有堵住
            if min(side_location) < 0 or max(side_location) >= 15:
                return False
            else:
                return False if self.table[side_location[0]][side_location[1]] == opt else True

        opt = B if sd == W else W
        bool_left = siding(fir)
        bool_right = siding(sec)
        if bool_left:
            block = 0 if bool_right else 2
        else:
            block = 1 if bool_right else 3
        return block

    @timing
    def line_ordering(line):
        def get_ind():
            rate = 1
            chess_type_index_of_lc = 0
            for item in chesses[::-1]:
                if item != 2:
                    chess_type_index_of_lc += rate
                rate *= 2
            return chess_type_index_of_lc

        # 将连续五颗字整型，仅用于 self.aoe 函数
        chesses = [self.table[item[0]][item[1]] for item in line]

        if W in chesses and B in chesses:
            return False

        left = [line[0][0] * 2 - line[1][0], line[0][1] * 2 - line[1][1]]
        right = [line[-1][0] * 2 - line[-2][0], line[-1][1] * 2 - line[-2][1]]

        if B in chesses:
            situation = get_ind()
            if situation == 31:
                # 5连了
                self._winning(B, line=line, show=show)
            n_block = get_offset_by_block(left, right, B)
            return [B, line, chesses, situation, LC[situation][n_block]]
        elif W in chesses:
            situation = get_ind()
            if situation == 31:
                self._winning(W, line=line, show=show)
            n_block = get_offset_by_block(left, right, W)
            return [W, line, chesses, situation, LC[situation][n_block]]
        else:
            return False

    @timing
    def line_filter(line_input):
        def line_cutter(_line):
            ret = []
            flag = _line[0]
            tmp = [flag]
            for x in _line[1:]:
                if x == flag:
                    tmp.append(x)
                else:
                    ret.append(tmp)
                    tmp = [x]
                    flag = x
            ret.append(tmp)
            return ret

        def line_grouper(_line):
            ret = line_cutter(_line)

            fin = set([0])
            offset = 0
            for ind, line in enumerate(ret):
                lg = len(line)
                if line[0] == 2:
                    offset += lg
                    continue
                if ind > 0 and ret[ind - 1][0] == 2:
                    start = offset - 5 + lg
                    if start >= 0:
                        fin.add(start)
                if ind < len(ret) - 1 and ret[ind + 1][0] == 2:
                    fin.add(offset)
                if lg >= 5:
                    fin.add(offset)
                offset += lg
            fin = [line_input[i: i + 5] for i in fin]
            return fin

        inp = [self.table[row][col] for row, col in line_input]
        return line_grouper(inp)

    ret = []
    changes = dict()
    self.sub_score[row][col] = [0, 0, 0, 0, 0, 0, 0, 0]

    aoe_line = self.ways[row * 15 + col]
    for direction in range(4):
        tmp_line = aoe_line[direction]
        for new_row, new_col in tmp_line:
            self.sub_score[new_row][new_col][direction] = 0
            self.sub_score[new_row][new_col][direction + 4] = 0

        for l in line_filter(tmp_line):
            if len(l) == 5:
                ordered_line = line_ordering(l)
                if ordered_line:
                    ret.append([direction, ordered_line])

    for l in ret:
        direction, [sid, locations, _, _, result] = l
        for ind, loc in enumerate(locations):
            key = (sid, direction, loc)
            if key in changes:
                changes[key] = max(int(result[ind]), changes[key])
            else:
                changes[key] = int(result[ind])
    for k, v in changes.items():
        sid, direction, (row, col) = k
        offset = sid * 4 + direction
        self.sub_score[row][col][offset] = v

    for direction in range(4):
        tmp_line = aoe_line[direction]
        for row, col in tmp_line:
            values = self.sub_score[row][col]
            self.score[row][col] = four_to_one(values)

    self._gen()
    self.set_zob()



class Base:
    def evaluate(self):
        self.score = [0, 0]
        black_score = self.score[B] - self.score[W]

        last_loc = self.records[-1]
        current_player = self.table[last_loc[0]][last_loc[1]]  # 刚刚落子的一方

        return {
            B: black_score,
            W: black_score * -1,
        }[current_player]


class BGValues:
    def __init__(self, width=15):
        self.width = width
        self.values = {
            B: defaultdict(list),
            W: defaultdict(list)}
        self.__lines = []
        self.table = []
        self.__diagonals = get_diagonals(self.width)
        print(self.__diagonals)

    @timing
    def upgrade(self, table):
        self.table = table
        self.__lines = []
        self.values = {
            B: defaultdict(list),
            W: defaultdict(list)}
        self.__make_lines()

    @timing
    def __chess(self, line, loc, cell):
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
                self.__lines.append(line)
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
            self.__lines.append(line)
            line = [
                [loc],  # 0：棋子
                [],  # 1：第一边空
                [],  # 2：中空
                [],  # 3：第二边空
                cell,  # 4：棋子颜色
            ]
            # 一行看完，清算
        return line

    @timing
    def __line_grouping(self, line, chess):
        t = len(line[0])
        t = 6 if t >= 6 else t
        if line[1] and line[3]:
            key = "活" + str(t) if t + len(line[2]) <= 4 else "冲" + str(t)
        elif line[1] or line[2] or line[3]:
            if t == 1:
                return
            key = "冲" + str(t)
        else:
            return
        sli = ADR[len(line[2])][key]
        line[1] = line[1][:sli]
        line[3] = line[3][:sli]
        format_line = line[1] + line[2] + line[3]
        self.values[chess][key].append(format_line)

    @timing
    def __make_lines(self):
        for sid in (True, False):
            for row in range(self.width):
                line = [
                    [],  # 0：棋子
                    [],  # 1：第一边空
                    [],  # 2：中空
                    [],  # 3：第二边空
                    False,  # 4：棋子颜色
                ]
                for col in range(self.width):
                    loc = (row, col) if sid else (col, row)
                    cell = self.table[row][col] if sid else self.table[col][row]
                    line = self.__chess(line, loc, cell)

                # 一行看完，清算
                self.__lines.append(line)

        for diagonal in self.__diagonals:
            line = [
                [],  # 0：棋子
                [],  # 1：第一边空
                [],  # 2：中空
                [],  # 3：第二边空
                False,  # 4：棋子颜色
            ]
            for loc in diagonal:
                cell = self.table[loc[0]][loc[1]]
                line = self.__chess(line, loc, cell)

            self.__lines.append(line)

        final = []
        for line in self.__lines:
            if not line[0]:
                continue
            if sum([len(i) for i in line[:4]]) < 5:
                continue
            space = line[1] + line[2] + line[3]
            if not space:
                continue
            line[1].reverse()
            final.append(line)
        for line in final:
            self.__line_grouping(line, line[4])


class BaseGame:
    def __init__(self, restricted=True, manual=[]):
        self.winner = False
        self.width = 15
        self.table = []
        for i in range(self.width):
            self.table.append([0] * self.width)
        self.records = []
        self.step = 0
        self.restricted = restricted
        self.values = {
            B: defaultdict(list),
            W: defaultdict(list)}
        self.check = []

        self.zob_grid = []
        self.zob_key = 0
        ra = 2 ** 105
        for i in range(self.width):
            t = []
            for j in range(self.width):
                t1 = []
                for k in range(3):
                    t1.append(int(random.random() * ra))
                t.append(t1)
            self.zob_grid.append(t)
        self.translation_table = dict()

        if manual:
            self.width = len(manual)
            if [len(item) for item in manual] == [self.width] * self.width:
                self.table = manual
                self.step = 0
                for row, line in enumerate(manual):
                    for col, cell in enumerate(line):
                        self.zob_key ^= self.zob_grid[row][col][cell]
                        if cell != 0:
                            self.step += 1
            else:
                raise TypeError
        self.tmp_gen = BGValues(self.width)

    def get_zob(self):
        k = self.zob_key
        if k in self.translation_table:
            return self.translation_table[k]
        else:
            return False

    def restart(self):
        self.__init__()

    @timing
    def modify_values(self, loc, player):
        row, col = loc
        opponent = W if player == B else B

        for direction in range(4):
            # 计算自己新增的 line， 以及对方受影响的棋子（opt）
            line, opt = self.base_linear(row, col, player, direction, modify=True)
            self.values = self.inside_line_grouping(line, player, values=self.values)
            if opt:
                # 假如有对方的棋子受影响，对应的 line 需要重算
                opt_line = self.base_linear(opt[0], opt[1], opponent, direction)
                self.values = self.inside_line_grouping(opt_line, opponent, values=self.values)

        # 落子之后，对方一些 line 被破坏了，上面落子时已经重算了，这里直接全部删掉
        for sid, d in self.values.items():
            for key, v in d.items():
                self.values[sid][key] = [l for l in v if loc not in l]


    @timing
    def inside_line_grouping(self, line, chess, values):
        t = len(line["s"])
        t = 6 if t >= 6 else t
        if line[-1] and line[1]:
            key = "活" + str(t) if t + len(line[0]) <= 4 else "冲" + str(t)
        elif line[0] or line[1] or line[-1]:
            if t == 1:
                return values
            key = "冲" + str(t)
        else:
            return values
        sli = ADR[len(line[0])][key]
        line[-1] = line[-1][:sli]
        line[1] = line[1][:sli]
        format_line = line[-1] + line[0] + line[1]
        values[chess][key].append(format_line)
        return values

    @timing
    def judge(self, loc, player, show=True):
        pass
        # if show:
            # logger.info("{:<12}{}".format(info, self.records))
        # else:
            # logger.debug("{:<12}{}".format(info, self.records))

    @timing
    def move(self, loc, show=True):
        if isinstance(loc, str):
            loc = list(map(int, loc.split(",")))
        if self.winner:
            return False
        if max(loc) >= self.width or min(loc) < 0:
            logger.error("子落棋盘外")
            return False
        row, col = loc
        if self.table[row][col] != 0:
            logger.error("这个位置已经有棋了")
            return False
        self.step += 1
        player = B if self.step % 2 == 1 else W
        self.table[row][col] = player
        self.zob_key ^= self.zob_grid[row][col][0] ^ self.zob_grid[row][col][player]
        self.records.append(loc)
        self.judge(loc, player, show=show)
        return True

    def undo(self, count=1):
        if len(self.records) < count:
            logger.error("悔棋失败！！！！！")
            return
        for i in range(count):
            row, col = self.records.pop()
            tmp = self.table[row][col]
            self.table[row][col] = 0
            self.zob_key ^= self.zob_grid[row][col][tmp] ^ self.zob_grid[row][col][0]
        self.winner = False
        self.step -= count

    def inside_make_line(self):
        self.tmp_gen.upgrade(self.table)
        self.values = self.tmp_gen.values

