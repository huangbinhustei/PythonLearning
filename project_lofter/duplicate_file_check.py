#!/usr/bin/env python3

import hashlib
import os
from PIL import Image
import time
from functools import wraps
from collections import defaultdict
import shutil

basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "check_target")
folder_length = defaultdict(lambda: 0)
danger_folder = defaultdict(lambda: 0)
safedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "safe")


def cost_count(func):
    @wraps(func)
    def costing(*args, **kw):
        start_time = time.time()
        ret = func(*args, **kw)
        time_cost = int((time.time()-start_time) * 10000000)
        print("Func(" + str(func.__name__) + ")\tcost: " + str(time_cost) + " μs")
        return ret
    return costing


@cost_count
def single_folder_remove():
    """
        1.假如某个文件夹下面只有一张图片，将图片移动到上一级文件夹。
        2.移动图片后，假如该文件夹没有子目录，那么将他移动到 safe 目录，准备手动删除。
        3.这个函数可能需要执行多次。
        4.同名文件夹需要手动删除。
    :return:
    """

    maybe_empty_folder = []
    all_pictures, all_folders = loading()

    for this_folder, target_file in danger_folder.items():
        target_folder = os.path.abspath(os.path.join(this_folder, os.pardir))
        shutil.move(target_file, target_folder)

        remains = next(os.walk(this_folder))
        maybe_empty_folder.append([this_folder, remains[1], remains[2]])

    flag = False
    for line in maybe_empty_folder:
        if len(line[1]) == 0:
            try:
                shutil.move(line[0], safedir)
                flag = True
            except:
                print("同名文件夹!\n\t" + line[0] + ":移动失败")
    if flag:
        print("最好再运行一次")


@cost_count
def duplicate_file_check(all_pictures):
    """
        1.从文件大小/图片尺寸/MD5三个维度判断是否重复。
        2.发现去掉『图片尺寸』这个去重纬度，速度反而变快了。
    :return: md5_value:[pic1, pic2 ...]
    """

    md5_pictures = defaultdict(lambda: [])

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

        def md5(f_name):
            m = hashlib.md5()
            with open(f_name, "rb") as f:
                m.update(f.read())
            return m.hexdigest()

        dd = defaultdict(lambda: [])
        for item in f_list:
            dd[md5(item)].append(item)
        return dd

    # for size, pic_list_1 in size_grouping(all_picture).items():
    #     if len(pic_list_1) <= 1:
    #         continue
    #     for img_size, pic_list_2 in img_size_grouping(pic_list_1).items():
    #         if len(pic_list_2) <= 1:
    #             continue
    #         for md, pic_list_3 in md5_grouping(pic_list_2).items():
    #             if len(pic_list_3) <= 1:
    #                 continue
    #             md5_pictures[md] = pic_list_3

    for size, pic_list_1 in size_grouping(all_pictures).items():
        if len(pic_list_1) <= 1:
            continue
        for md, pic_list_3 in md5_grouping(pic_list_1).items():
            if len(pic_list_3) <= 1:
                continue
            md5_pictures[md] = pic_list_3

    return md5_pictures


@cost_count
def folder_similar_check(md5_dict):

    def similarity_filter(t_dict, min_n):
        """
        :param t_dict:
         t_dict的结构：
        folder_A： {
            foler_B: n，其中 n 是相同文件的数量
            foler_C: n，其中 n 是相同文件的数量
        }
        :param min_n:
        :return:假如 n 过小，认为两个文件夹不相同，就过滤掉
        """
        if min_n <= 1:
            return t_dict

        for folder, folder_dict in t_dict.copy().items():
            for k1, v1 in folder_dict.copy().items():
                if min_n - 1 == v1:
                    del folder_dict[k1]
        for folder, folder_dict in t_dict.copy().items():
            if len(folder_dict) == 0:
                del t_dict[folder]
        return t_dict

    folder_group = defaultdict(lambda: defaultdict(lambda: 0))
    for t_md5, pic_list in md5_dict.items():
        folders = [os.path.abspath(os.path.join(pic, os.path.pardir)) for pic in pic_list]
        for t_fold in folders:
            temp = folders.copy()
            temp.remove(t_fold)
            for item in temp:
                if item not in folder_group and item != t_fold:
                    folder_group[t_fold][item] += 1

    folder_group = similarity_filter(folder_group, 1)

    for k, v in folder_group.items():
        print(k)
        for k1, v1 in v.items():
            print("\t" + k1 + "\t" + str(v1))


@cost_count
def loading():

    """
    目标是获得：
        all_pictures:所有图片列表
        all_folders:所有文件夹列表 -> 没发现有什么用
    :return:
    """

    all_pictures = []
    all_folders = []

    temp_dict = defaultdict(lambda: [])
    for item in os.walk(basedir):
        t_pardir, t_child_dir, t_files = item
        for s_file in t_files:
            if s_file[-3:] in ("jpg", "gif", "png"):
                temp_dict[t_pardir].append(os.path.join(t_pardir, s_file))
                all_pictures.append(os.path.join(t_pardir, s_file))
        for k, v in temp_dict.items():
            if len(v) == 1:
                danger_folder[k] = v[0]
        for s_file in t_child_dir:
            all_folders.append(os.path.join(t_pardir, s_file))
    return all_pictures, all_folders


def folder_thin():
    all_pictures, all_folders = loading()

    save_disk = 0
    need_del = []

    for f in all_folders:
        pic_in_f = next(os.walk(f))[2]
        pic_in_f = [os.path.join(f, item) for item in pic_in_f]
        result_dict = duplicate_file_check(pic_in_f)
        for k, v in result_dict.items():
            if len(v) == 1:
                continue
            need_del += v[1:]
    print("\n".join(need_del))

    for item in need_del:
        save_disk += os.path.getsize(item)
        # os.remove(item)
        # 抽样调查几个之后，就可以去掉注释，真的删文件了

    print("\nsave disk up to:" + str(save_disk))


def my_duplicate():
    all_pictures, all_folders = loading()
    md5_dict = duplicate_file_check(all_pictures)
    folder_similar_check(md5_dict)


if __name__ == '__main__':
    """
    三个主要函数：
    1. single_folder_remove：假如目录只包含一张图片，删除该目录，将图片移动到上级目录。
    2. folder_thin：在同一个目录内，删除重复图片。
    3. my_duplicate：看哪些目录拥有相同的图片，他们也许可以合并成一个目录。
    """
    # single_folder_remove()
    # folder_thin()
    my_duplicate()



