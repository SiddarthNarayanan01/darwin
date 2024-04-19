from collections import deque
from math import floor
from multiprocessing import Process
from typing import List, Tuple

import aiohttp
from darwin.configuration import DarwinConfig
from darwin.specification import parse_spec
from darwin.taskmaster.server import (
    EvaluationServer,
    EvolverServer,
    PostProcessorServer,
    SamplerServer,
    Server,
)


class DarwinClient:
    def __init__(self, spec: str, config: DarwinConfig) -> None:
        self.evolve_function, self.solve_function = parse_spec(spec, config.parse)
        self.spec = spec
        self.config = config
        self.task_queue = deque()
        self.session = aiohttp.ClientSession()
        self.samplers: List[Tuple[str, int]] = []
        self.postprocessors: List[Tuple[str, int]] = []
        self.evaluators: List[Tuple[str, int]] = []
        self.processes = []


    # TODO: Simplify start evolution process
    # Make more modular / distribute across more functions
    def start_evolution(self):
        # Create samplers
        self.spawn_samplers()
        # Create post processors
        self.spawn_postprocessors()
        # Create evaluators
        for i in range(self.config.eval.n_evaluators):
            # TODO: Pass optional kwargs from eval config to eval server
            # TODO: Figure out how to spawn them on localhost (avoid conflicts)
            # Avoid conflicts, configurable in respective config objects. Same applies
            # to other server types
            # If you are wondering how to pass kwargs -> **kwargs as last paramater
            s = EvaluationServer("127.0.0.1", 14232 + i, self.solve_function)
            self.evaluators.append(("127.0.0.1", 14232 + i))
            self.start_server(s)

        # Create the evovler
        # TODO: Pass optional kwargs from evolve config to evolve server
        evolver = EvolverServer(
            "127.0.0.1", 11111, self.config.evolve, self.evolve_function
        )
        # TODO: Actually implement the task queue / evolution logic with the task classes from taskmaster

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
                # TODO: Pass optional kwargs from sampler config to sampler server
                s = SamplerServer("127.0.0.1", 12345 + i, self.config.sample.backend, m)
                self.samplers.append(("127.0.0.1", 12345 + i))
                self.start_server(s)

    def spawn_postprocessors(self):
        if not self.config.postprocess.model_distribution:
            for i in range(self.config.postprocess.n_postprocessors):
                # TODO: Pass optional kwargs from postprocessors config to postprocessors server
                s = PostProcessorServer(
                    "127.0.0.1",
                    9147 + i,
                    verify_only=True,
                )
                self.postprocessors.append(("127.0.0.1", 9147 + i))
            return

        # TODO: Is there a better way of spawning servers that have a model_distribution property?
        md = self.config.postprocess.model_distribution
        pp_left = self.config.postprocess.n_postprocessors
        for i, m in enumerate(sorted(list(md.keys()), key=lambda x: md[x])):
            if i == len(md.keys()) - 1:
                n = pp_left
            else:
                n = floor(self.config.postprocess.n_postprocessors * md[m])
            pp_left -= n
            for i in range(n):
                # TODO: Pass optional kwargs from postprocessors config to postprocessors server
                s = PostProcessorServer(
                    "127.0.0.1",
                    9147 + i,
                    False,
                    backend=self.config.sample.backend,
                    model=m,
                )
                self.postprocessors.append(("127.0.0.1", 9147))
                self.start_server(s)

    # TODO: We should also handle graceful termination of servers (self.app.shutdown() in server)
    def start_server(self, s: Server):
        process = Process(target=s.start_server)
        process.start()
        self.processes.append(process)
