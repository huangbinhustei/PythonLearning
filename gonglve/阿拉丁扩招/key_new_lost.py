#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re

path = os.path.abspath('.')
file_new = os.path.join(path, "new.txt")
file_old = os.path.join(path, "keys_of_ald.txt")

par = re.compile(r'[a-z]+')

with open(file_old, "r") as f:
    keys_old = f.readlines()
keys_old = set(keys_old)
print(len(keys_old))

with open(file_new, "r") as f:
    keys_new = f.readlines()
keys_new = set(keys_new)
print(len(keys_new))

need_check = []

for item in [title for title in keys_new if title not in keys_old]:
    if len(item) < 3 or "www" in item or "com" in item:
        continue
    if len(re.sub(par, "", item)) < len(item):
        continue
    if item.replace("作文", "").replace(" ", "").replace(",", "").replace("，", "") in keys_old:
        continue
    need_check.append(item)

with open(os.path.join(path, "output_keys_add.txt"), "w") as f:
    for item in need_check:
        f.write(item)

with open(os.path.join(path, "output_keys_lost.txt"), "w") as f:
    for item in keys_old:
        if item not in keys_new:
            f.write(item)
