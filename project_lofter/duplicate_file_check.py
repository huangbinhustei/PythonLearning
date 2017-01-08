#!/usr/bin/env python3

import hashlib
import os
import time
from functools import wraps
from collections import defaultdict
import shutil
from PIL import Image

folder_length = defaultdict(lambda: 0)
basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "collated_by_folder")
too_big_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "big")


def cost_count(func):
    @wraps(func)
    def costing(*args, **kw):
        start_time = time.time()
        ret = func(*args, **kw)
        time_cost = int((time.time()-start_time) * 1000)
        if time_cost > 10:
            print("Func(" + str(func.__name__) + ")\tcost: " + str(time_cost) + " ms")
        return ret
    return costing


@cost_count
def remove_folder_thar_less_than_one_file():
    for t_folder in loading()[1]:
        if t_folder == basedir:
            continue
        xx, remain_folder, remain_files = next(os.walk(t_folder))
        if not remain_files and not remain_folder:
            os.rmdir(t_folder)
        if len(remain_files) == 1:
            the_file = os.path.join(t_folder, remain_files[0])
            target_folder = os.path.abspath(os.path.join(t_folder, os.pardir))
            shutil.move(the_file, target_folder)
            os.rmdir(t_folder)


@cost_count
def duplicate_file_check(all_pictures):
    """
    :return: md5_value:[pic1, pic2 ...]
    """
    md5_pictures = defaultdict(lambda: [])

    def md5(f_name):
        m = hashlib.md5()
        with open(f_name, "rb") as f:
            m.update(f.read())
        return m.hexdigest()

    for this_file in all_pictures:
        md5_pictures[md5(this_file)].append(this_file)

    for key_md5, pics in md5_pictures.copy().items():
        if len(pics) <= 1:
            del md5_pictures[key_md5]

    return md5_pictures


def folder_merge(t_dict):
    for folder_outer, value in t_dict.items():
        for folder_inner, v in value.items():
            pic_in_f = next(os.walk(folder_inner))[2]
        for item in pic_in_f:
            if os.path.exists(os.path.join(folder_outer, item)):
                print("目标文件夹有同名文件，直接删掉")
                os.remove(os.path.join(folder_inner, item))
            else:
                shutil.move(os.path.join(folder_inner, item), folder_outer)


def folder_similar_check(md5_dict):
    """
    :return:dict_of_this:
        folder_A： {
            folder_B: n，其中 n 是相同文件的数量
            folder_C: n，其中 n 是相同文件的数量
        }
    """

    def chain_reaction(t_dict):
        key_set_outer = set([item[0] for item in t_dict.items()])
        if basedir in t_dict:
            del t_dict[basedir]
        for key_outer, value in t_dict.copy().items():
            for key_inner, s_value in value.copy().items():
                if key_inner in key_set_outer:
                    del value[key_inner]

        for key_outer, value in t_dict.copy().items():
            if not value:
                del t_dict[key_outer]
        return t_dict

    def step_one(t_md5_dict):
        t_folder_group = defaultdict(lambda: defaultdict(lambda: 0))
        for t_md5, pic_list in t_md5_dict.items():
            folders = [os.path.abspath(os.path.join(pic, os.path.pardir)) for pic in pic_list]
            for t_fold in folders:
                temp = folders.copy()
                temp.remove(t_fold)
                for item in temp:
                    if item not in t_folder_group and item != t_fold:
                        t_folder_group[t_fold][item] += 1
        return t_folder_group

    folder_group = step_one(md5_dict)
    folder_group = chain_reaction(folder_group)

    return folder_group


def loading():
    """
    目标是获得：
        all_pictures:所有图片列表
        all_folders:所有文件夹列表 -> 没发现有什么用
    :return:
    """

    all_pictures = []
    all_folders = []
    for item in os.walk(basedir):
        t_pardir, t_child_dir, t_files = item
        for s_file in t_files:
            all_pictures.append(os.path.join(t_pardir, s_file))
        for s_file in t_child_dir:
            all_folders.append(os.path.join(t_pardir, s_file))
    return all_pictures, all_folders


@cost_count
def duplicate_in_folder():
    all_pictures, all_folders = loading()
    need_del = []

    for f in all_folders:
        pic_in_f = next(os.walk(f))[2]
        pic_in_f = [os.path.join(f, item) for item in pic_in_f]
        result_dict = duplicate_file_check(pic_in_f)
        for k, v in result_dict.items():
            if len(v) == 1:
                continue
            need_del += v[1:]

    save_disk = 0
    for item in need_del:
        save_disk += os.path.getsize(item)
        os.remove(item)

    if save_disk > 0:
        print("\nsave disk up to:" + str(save_disk / 1024 / 1024) + "MB")


@cost_count
def my_duplicate():
    all_pictures, all_folders = loading()
    md5_dict = duplicate_file_check(all_pictures)
    folder_g = folder_similar_check(md5_dict)
    folder_merge(folder_g)
    duplicate_in_folder()
    remove_folder_thar_less_than_one_file()


@cost_count
def remove_all_small_pic_and_log():
    all_pictures, all_folders = loading()
    save_disk = 0
    for item in all_pictures:
        if os.path.getsize(item) < 1000000:
            save_disk += os.path.getsize(item)
            os.remove(item)
        if ".txt" in item:
            save_disk += os.path.getsize(item)
            os.remove(item)
    if save_disk > 0:
        print("\nsave disk up to:" + str(save_disk / 1024 / 1024) + "MB")


def move_gif(folders):
    gif_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "GIF")
    if not os.path.exists(gif_folder):
        os.mkdir(gif_folder)
    gif_count = 0
    for pic in next(os.walk(folders))[2]:
        p_pic = os.path.join(folders, pic)
        img = Image.open(p_pic)
        pic_type = img.format
        img.close()
        if pic_type == "GIF":
            gif_count += 1
            shutil.move(p_pic, gif_folder)
    return gif_count


if __name__ == '__main__':
    # remove_all_small_pic_and_log()  # 删掉过小的文件和log.txt，这个只需要做一次
    # duplicate_in_folder()   # 同一文件夹去重
    # remove_folder_thar_less_than_one_file()     # 删除空目录，假如目录内只有一张图片，将图片剪切到父目录，再删除自己
    # my_duplicate()
    gifs = 0
    for fo in loading()[1]:
        gifs += move_gif(fo)
    print(gifs)

