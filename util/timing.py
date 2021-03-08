import time


def time_it(func, msg):
    time_start = time.time()
    res = func()
    time_end = time.time()
    print(msg.format(time_end - time_start))
    return res