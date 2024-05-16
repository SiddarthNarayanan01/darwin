from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager, Queue

def add(queue):
    sum = 0
    for i in range(int(1e8)):
        sum += i
    queue.put(sum)


if __name__ == "__main__":
    pool = ProcessPoolExecutor(max_workers=10)
    queue = Manager().Queue()

    for i in range(10):
        pool.submit(add,queue)

    count = 10
    while count:
        if not queue.empty():
            print(queue.get(block=False))
            count -= 1
