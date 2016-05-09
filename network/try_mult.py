import threading
import random
from time import sleep, ctime
from multiprocessing import Process, Queue, Pool, Manager
import os
chr_need_print_1 = ("-1", "-2", "-3", "-4")
chr_need_print_2 = ("1", "2", "3", "4")


def print_char(char):
    print(str(os.getpid()) + "\t" + str(threading.current_thread().name) + "\tstart")
    me_t = random.uniform(0, 6)
    # print(char + "\tstart\t@\t" + str(ctime() + "\t& will sleep\t" + str(me_t)[:4]))
    sleep(me_t)
    print(str(os.getpid()) + "\t" + str(threading.current_thread().name) + "\t停！！！！！！")
    # print(char + "\tend\t@\t" + str(ctime()))


def me_threading(big_item):
    th = []
    for item in chr_need_print_1:
        th.append(threading.Thread(target=print_char, args=(big_item + item,)))
    for t in th:
        t.setDaemon(True)
        t.start()
    for t in th:
        t.join()


def me_multiprocessing_need_manager_queue():
    # 其他多进程用法都请见 recommending/init_index.py
    # 坑：   一旦使用了Pool，就不能使用queue了，而需要使用Manager().Queue()，并且Manager().Queue()会算一个进程。
    p = Pool(4)
    for item in chr_need_print_1:
        p.apply_async(me_threading, args=(item,))
        sleep(1)
    p.close()
    p.join()    # 假如没有join，主进程会直接运行结束并顺手杀掉子进程


def me_multiprocessing_need_queue():
    # 其他多进程用法都请见 recommending/init_index.py
    # 可以直接使用queue同步数据
    p_fi = Process(target=me_threading, args=(chr_need_print_2[0],))
    p_fi.daemon = True
    p_fi.start()

    p_se = Process(target=me_threading, args=(chr_need_print_2[1],))
    p_se.daemon = True
    p_se.start()

    p_fi.join()
    p_se.join()


if __name__ == "__main__":
    me_multiprocessing_need_manager_queue()


