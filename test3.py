import concurrent.futures
import time

number_of_tasks = 0

class Sampler:
    def prompt(self, c):
        global number_of_tasks
        print(c)
        time.sleep(2)
        number_of_tasks -= 1


if __name__ == "__main__":
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=24)
    task = Sampler()
    i = 0
    count = []
    while True:
        if number_of_tasks < 50:
            count.append(pool.submit(task.prompt, i))
            number_of_tasks += 1
            i += 1
        time.sleep(0.01)
