#!/usr/bin/env python3

import hashlib
import os
from PIL import Image
from collections import defaultdict
import time
import re

# top_path = "D:\\Project\\PythonLearning\\project_lofter\\"
top_path = "D:/Project/PythonLearning/project_lofter/"
log_file = "D:/Project/PythonLearning/project_lofter/log.txt"
log_file_folder_dict = "D:/Project/PythonLearning/project_lofter/log_file_folder_dict.txt"


def md5(f_name):
    m = hashlib.md5()
    with open(f_name, "rb") as f:
        m.update(f.read())
    return m.hexdigest()


def get_files(path):
    files = []
    for item in os.walk(path):
        for s_item in item[2]:
            files.append(os.path.join(item[0], s_item))
    return list(set(files))


def size_grouping(f_list):
    dd = defaultdict(lambda: [])
    for file in f_list:
        dd[os.path.getsize(file)].append(file)
    return dd


def img_size_grouping(f_list):
    dd = defaultdict(lambda: [])
    for item in f_list:
        try:
            img = Image.open(item)
            dd[img.size].append(item)
        except:
            pass
    return dd


def md5_grouping(f_list):
    dd = defaultdict(lambda: [])
    for item in f_list:
        dd[md5(item)].append(item)
    return dd


def duplicate_file_check():
    """
    从文件大小/图片尺寸/MD5三个维度判断是否重复
    :return:
    """
    with open(log_file, "w") as f:
        for k, v in size_grouping(get_files(top_path)).items():
            if len(v) <= 1:
                continue
            for k1, v1 in img_size_grouping(v).items():
                if len(v1) <= 1:
                    continue
                for k2, v2 in md5_grouping(v1).items():
                    if len(v2) <= 1:
                        continue
                    temp = k2 + "\t" + ",".join(v2).replace(top_path, "")
                    print(temp, file=f)


def folder_similar_check():
    folders = []
    re_par = re.compile(r'.[a-z,0-9,A-Z]{32}\.jpg')
    # folder_dict: 第一位存文件夹包含的文件总量，第二个词典存重复文件所在的其他文件夹
    folder_dict = defaultdict(lambda: [0, defaultdict(lambda: 0)])
    with open(log_file, "r") as f:
        # 获取 folder 列表，格式是"['wzwdkcm\\6a889_a27c231', 'wzwdkcm\\6a889_a27c232', '']"
        for item in f.readlines():
            ha = item.strip().replace(",", "").split("\t")
            # \t前的是文件的MD5，没有价值。
            rows = re.sub(re_par, "\t", ha[1])
            folders.append(rows.split("\t"))
    for rows in folders:
        # folder 列表 → folder_dict
        # 这里貌似有点问题，一个文件夹既有可能在前面，又有可能在后面
        temp = os.walk(os.path.join(top_path, rows[0][1:]))
        temp = next(temp)
        folder_dict[rows[0]][0] = len(temp[2]) - 1
        for s_folder in rows[1:]:
            if s_folder == "":
                continue
            folder_dict[rows[0]][1][s_folder] += 1
    # remove_single_file_folder(folder_dict)
    with open(log_file_folder_dict, "w") as f:
        for k, v in folder_dict.items():
            print(str(v[0]) + "\t" + k, file=f)
            for s_k, s_v in v[1].items():
                print("\t" + str(s_v) + "\t" + s_k, file=f)


def remove_single_file_folder(this_folder_dict):
    '''
    假如某个文件夹下面只有一个文件（不算log.txt)
    且这个文件是重复的，那么直接删除这个文件就好了。
    :return:
    '''
    sum1 = 0
    for k, v in this_folder_dict.items():
        if v[0] == 1:
            temp = os.walk(os.path.join(top_path, k))
            temp = next(temp)
            # t_file = top_path + k + "/" + temp[2][0]
            t_file = os.path.join(os.path.join(top_path, k), temp[2][0])
            print(t_file)
            temp = os.path.getsize(t_file)
            sum1 += temp
            print(str(temp) + "\t" + t_file)
    print(str(sum1))
    os.remove(t_file)


if __name__ == '__main__':
    times = 0
    a = time.time()
    # duplicate_file_check()    #这个已经完成了
    folder_similar_check()
    times += (time.time() - a)
    print(times)
