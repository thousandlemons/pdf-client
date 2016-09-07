import random
import time
from concurrent import futures
from threading import Thread


class JobRunner(Thread):
    def __init__(self, executor):
        super().__init__()
        self.executor = executor

    def run(self):
        future_list = []

        for i in range(20):
            print("Submitted {i}".format(i=i))
            future_list.append(self.executor.submit(mock_long_io, i))
            time.sleep(0.1)

        for future in futures.as_completed(future_list):
            print("Completed {i}".format(i=future.result()))


class MultiThreadJobRunner(Thread):
    max_workers = None


def mock_long_io(i):
    print("Processing {i}".format(i=i))
    time.sleep(random.uniform(1, 10))
    return i


def main():
    executor = futures.ThreadPoolExecutor(max_workers=5)
    job_submitter = JobRunner(executor)
    job_submitter.start()


main()
