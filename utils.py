import time

def timeit(func, *args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    result['time_taken'] = round(end - start, 6)
    return result
