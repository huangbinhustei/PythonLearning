#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

path = os.path.abspath('.')
file_new = os.path.join(path,input("former_keys_file_name:\t"))
file_old = os.path.join(path,input("new_keys_file_name:\t"))

with open(file_old,"r") as f:
	keys_old = f.readlines()
keys_old = set(keys_old)

with open(file_new,"r") as f:
	keys_new = f.readlines()
keys_new = set(keys_new)

with open(os.path.join(path, "output_keys_add.txt"),"w") as f:
	for item in keys_new:
		if item not in keys_old:
			f.write(item)

with open(os.path.join(path, "output_keys_lost.txt"),"w") as f:
	for item in keys_old:
		if item not in keys_new:
			f.write(item)