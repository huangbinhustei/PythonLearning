import threading
import random
from time import sleep, ctime
from multiprocessing import Process, Queue, Pool, Manager
import asyncio
import requests
chr_need_print = ("a", "BB", "一", "甲子")


def print_char(char):
    me_t = random.uniform(1.5, 2.5)
    print(char + "\tstart\t@\t" + str(ctime() + "\t& will sleep\t" + str(me_t)[0:4]))
    sleep(me_t)
    print(char + "\tend\t@\t" + str(ctime()))


def me_threading():
    th = []
    for item in chr_need_print:
        th.append(threading.Thread(target=print_char, args=(item,)))
    for t in th:
        t.setDaemon(True)
        t.start()
    for t in th:
        t.join()


def me_multiprocessing_need_manager_queue():
    # 其他多进程用法都请见 recommending/init_index.py
    # 坑：   一旦使用了Pool，就不能使用queue了，而需要使用Manager().Queue()，并且Manager().Queue()会算一个进程。
    p = Pool(4)
    for item in chr_need_print:
        p.apply_async(print_char, args=(item,))
    p.close()
    p.join()    # 假如没有join，主进程会直接运行结束并顺手杀掉子进程


def me_multiprocessing_need_queue():
    # 其他多进程用法都请见 recommending/init_index.py
    # 可以直接使用queue同步数据
    p_fi = Process(target=print_char, args=(chr_need_print[0],))
    p_fi.daemon = True
    p_fi.start()

    p_se = Process(target=print_char, args=(chr_need_print[1],))
    p_se.daemon = True
    p_se.start()

    p_fi.join()
    p_se.join()


async def me_async_print_char(char):
    me_t = random.uniform(0.5, 1.5)
    print(char + "\tstart\t@\t" + str(ctime() + "\t& will sleep\t" + str(me_t)[0:4]))
    await asyncio.sleep(me_t)   # await后面的函数得是一个协程才行
    print(char + "\tend\t@\t" + str(ctime()))


@asyncio.coroutine
def t_temp():
    # target = requests.get("http://niutuku.com/bizhi/9247/416438.shtml")
    sleep(2)
    # yield from sleep(2)

    # print(target.headers["Date"])


async def me_requests():
    print("requests\tstart\t@\t" + str(ctime()))
    await t_temp()
    print("requests\tend\t@\t" + str(ctime()))


def me_async():
    loop = asyncio.get_event_loop()
    tasks = [me_requests(), me_requests()]
    # tasks = [me_async_print_char("hahahaha"), me_requests()]
    # tasks = []
    # for item in chr_need_print:
    #     tasks.append(me_async_print_char(item))
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


if __name__ == "__main__":
    # me_threading()
    # me_multiprocessing_need_manager_queue()
    # me_multiprocessing_need_queue()
    me_async()


