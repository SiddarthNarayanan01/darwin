from multiprocessing.managers import DictProxy, ListProxy
from darwin.taskmaster.task import SampleTask
from darwin.sampling.backend import Backend
from time import sleep


class SampleProcess:
    def __init__(self, id: int, bridge: DictProxy[int, ListProxy], backend: Backend) -> None:
        self.id = id
        self.bridge = bridge
        self.backend = backend

    def run(self):
        while True:
            task: SampleTask = self.bridge[self.id][1]
            if task != None:
                self.bridge[self.id][2] = self.execute_task(task)
                self.bridge[self.id][1] = None
            sleep(2)

    def execute_task(self, task: SampleTask):
        return self.backend.prompt(task.prompt)
