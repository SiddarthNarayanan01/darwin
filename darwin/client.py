from collections import deque
from math import floor
from typing import List, Tuple

import aiohttp
from multiprocessing import Process
from darwin.configuration import DarwinConfig
from darwin.taskmaster.server import (
    EvaluationServer,
    EvolverServer,
    PostProcessorServer,
    SamplerServer,
)
from darwin.taskmaster.server import Server


class DarwinClient:
    def __init__(self, spec: str, base_function: str, config: DarwinConfig) -> None:
        self.spec = spec
        self.config = config
        self.base_function = base_function
        self.task_queue = deque()
        self.session = aiohttp.ClientSession()
        self.samplers: List[Tuple[str, int]] = []
        self.postprocessors: List[Tuple[str, int]] = []
        self.evaluators: List[Tuple[str, int]] = []
        self.processes = []

    def start_evolution(self):
        # Create samplers
        self.spawn_samplers()
        # Create post processors
        self.spawn_postprocessors()
        # Create evaluators
        for i in range(self.config.eval.n_evaluators):
            s = EvaluationServer("127.0.0.1", 14232 + i)
            self.evaluators.append(("127.0.0.1", 14232 + i))
            self.start_server(s)

        # Create the evovler
        evolver = EvolverServer(
            "127.0.0.1",
            11111,
            self.config.evolve,
        )

    def spawn_samplers(self):
        md = self.config.sample.model_distribution
        samplers_left = self.config.sample.n_samplers
        for i, m in enumerate(sorted(list(md.keys()), key=lambda x: md[x])):
            if i == len(md.keys()) - 1:
                n = samplers_left
            else:
                n = floor(self.config.sample.n_samplers * md[m])
            samplers_left -= n
            for i in range(n):
                s = SamplerServer("127.0.0.1", 12345 + i, self.config.sample.backend, m)
                self.samplers.append(("127.0.0.1", 12345 + i))
                self.start_server(s)

    def spawn_postprocessors(self):
        if not self.config.postprocess.model_distribution:
            for i in range(self.config.postprocess.n_postprocessors):
                s = PostProcessorServer(
                    "127.0.0.1",
                    9147 + i,
                    verify_only=True,
                )
                self.postprocessors.append(("127.0.0.1", 7135 + i))
            return

        md = self.config.postprocess.model_distribution
        pp_left = self.config.postprocess.n_postprocessors
        for i, m in enumerate(sorted(list(md.keys()), key=lambda x: md[x])):
            if i == len(md.keys()) - 1:
                n = pp_left
            else:
                n = floor(self.config.postprocess.n_postprocessors * md[m])
            pp_left -= n
            for i in range(n):
                s = PostProcessorServer(
                    "127.0.0.1",
                    9147 + i,
                    False,
                    backend=self.config.sample.backend,
                    model=m,
                )
                self.postprocessors.append(("127.0.0.1", 9147))
                self.start_server(s)

    def start_server(self, s: Server):
        process = Process(target=s.start_server)
        process.start()
        self.processes.append(process)
