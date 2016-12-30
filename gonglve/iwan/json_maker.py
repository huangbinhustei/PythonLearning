#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from collections import defaultdict
import json
import time

games = defaultdict(lambda: [])
basedir = os.path.abspath(os.path.dirname(__file__))


def load_to_dict():
    with open(os.path.join(basedir, "data", "mid_output.txt"), "r", encoding="utf-8") as f:
        file_content = [line.strip().split("\t") for line in f.readlines()]
    game_ids = set([line[1] for line in file_content])
    for game_id in game_ids:
        games[game_id] = [line for line in file_content if line[1] == game_id]
    for line in file_content:
        if "jpg" not in line[-1]:
            print("有空的缩略图")
            return False
    return True


def json_writing():
    for k, v in games.items():
        json_file_name = str(k) + ".txt"
        i = 0
        with open(os.path.join(basedir, "result", json_file_name), "w", encoding="utf-8") as f:
            for item in v:
                f.write(json.dumps(
                    dict(indexData=item[0],
                         title=item[4],
                         image=item[-1],
                         url=item[2],
                         pubtime=str(int(time.time()) + i),
                         category=item[3],
                         childCagegory="", ))+"\n")
                i += 1


if __name__ == '__main__':
    flag = load_to_dict()
    if flag:
        json_writing()
