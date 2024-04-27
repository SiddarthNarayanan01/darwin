import ast
import json
import time
from collections import deque
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Queue
from typing import Any, Deque, Dict, List, Tuple

import numpy as np
import requests
from darwin2.configuration.ollama import OllamaConfig
from darwin2.evolving.samples import Sample
from darwin2.evaluating.evaluator import Evaluator
from darwin2.evolving.evolver import Evolver
from darwin2.postprocessing.parser import RegExParser


class OllamaClient:
    def __init__(
        self,
        endpoints: List[str],
        config: OllamaConfig,
        corrector_endpoints: List[str] | None = None,
    ) -> None:
        self.endpoints = endpoints
        self.corrector_endpoints = corrector_endpoints or endpoints
        self.config = config
        self.evaluator = Evaluator()
        self.evolver = Evolver(config.evolve_config)

    def start(
        self,
        spec: str,
        evolve_function_name: str,
        solve_function_name: str,
        inputs: Tuple[Any, ...],
    ):
        """Start the evolution process

        This function creates the thread pools for the samplers, evaluators, and correctors, and starts the infinite evolution process.

        """
        self.spec = spec
        self.base_evolve_function, self.solve_function = self.__parse_spec(
            self.spec, evolve_function_name, solve_function_name
        )

        # Spawn samplers
        self.samplers = ThreadPoolExecutor(max_workers=self.config.n_samplers)

        if self.config.n_correctors:
            # Spawn correctors
            self.correctors = ThreadPoolExecutor(max_workers=self.config.n_correctors)
        # Spawn evaluators
        self.evaluators = ThreadPoolExecutor(max_workers=self.config.n_evaluators)

        samples_queue: Deque[Sample] = deque()
        corrections_queue: Deque[Sample] = deque()
        scores_queue: Queue = Queue()

        # Register base evolve function and score in all islands
        self.evaluators.submit(
            self.evaluator.eval,
            scores_queue,
            self.spec,
            Sample(self.base_evolve_function, -1),
            inputs,
            solve_function_name,
            evolve_function_name,
        )
        sample = scores_queue.get(block=True)
        self.evolver.populate_islands(sample)

        # Start infinite evolution loop
        n_sample_tasks = 0
        while True:
            if n_sample_tasks < 100:
                sample = self.__get_prompt_and_island_id()
                self.samplers.submit(
                    self.__sample,
                    samples_queue,
                    np.random.choice(self.endpoints, 1)[0],
                    sample,
                    self.__yield_weighted_model_name(self.config.samplers),
                )

            # Pass sample to correctors if needed
            if samples_queue:
                sample = samples_queue.popleft()
                sample.code = RegExParser.parse(sample.code)
                print("#"*20, "SAMPLE", "#"*20, sep="\n")
                if self.config.n_correctors > 0 and self.config.correctors:
                    self.correctors.submit(
                        self.__correct_sample,
                        corrections_queue,
                        np.random.choice(self.corrector_endpoints, 1)[0],
                        sample,
                        self.__yield_weighted_model_name(self.config.correctors),
                    )
                else:
                    # Must send to evaluators instead
                    self.evaluators.submit(
                        self.evaluator.eval,
                        scores_queue,
                        spec,
                        sample,
                        inputs,
                        solve_function_name,
                        evolve_function_name
                    )
                n_sample_tasks -= 1

            if corrections_queue:
                correction = corrections_queue.popleft()
                print("#"*20, "CORRECT", "#"*20, sep="\n")
                self.evaluators.submit(
                    self.evaluator.eval,
                    scores_queue,
                    spec,
                    correction,
                    inputs,
                    solve_function_name,
                    evolve_function_name
                )

            if not scores_queue.empty():
                sample = scores_queue.get()
                print("#"*20, f"SCORE: {sample.score}", "#"*20, sep="\n")
                self.evolver.register_sample(sample, [sample.score])

            time.sleep(0.01)

    def __yield_weighted_model_name(self, model_distribution: Dict[str, float]) -> str:
        return np.random.choice(
            list(model_distribution.keys()), 1, p=list(model_distribution.values())
        )[0]

    def __sample(
        self, samples_queue: Deque[Sample], endpoint: str, sample: Sample, model: str
    ):
        try:
            response = requests.post(
                endpoint,
                data=json.dumps(
                    {"prompt": sample.code, "model": model, "stream": False}
                ),
            ).json()["response"]
            samples_queue.append(Sample(response, sample.island_id))
        except:
            # If sample failed, return the base evolve function that was implemented in the spec
            samples_queue.append(
                Sample(
                    self.base_evolve_function,
                    sample.island_id,
                )
            )

    def __correct_sample(
        self,
        corrections_queue: Deque[Sample],
        endpoint: str,
        sample: Sample,
        model: str,
    ):
        prompt_aug = f"Correct this code to the best of your ability. If the code is fine as is, simply output the code in a markdown code block.\n\n {sample.code}"
        try:
            response = requests.post(
                endpoint,
                data=json.dumps(
                    {"prompt": prompt_aug, "model": model, "stream": False}
                ),
            ).json()["response"]
            sample.code = RegExParser.parse(response)
            corrections_queue.append(Sample(sample.code, sample.island_id))
        except:
            # If correction failed, return original sample
            corrections_queue.append(sample)


    def __get_prompt_and_island_id(self) -> Sample:
        prompt = "Below are older versions of the function. You are to use these versions to help you improve the function given your understanding of the function's job."
        samples, island_id = self.evolver.get_samples()
        for i in samples:
            prompt += "\n" + i
        prompt += "Generate an improved function. Format your response in markdown syntax with a python code block containing the improved function."
        return Sample(prompt, island_id)

    def __parse_spec(
        self, spec: str, evolve_function_name: str, solve_function_name: str
    ) -> tuple[str, str]:
        tree = ast.parse(spec)

        evolved_function = ""
        solve_function = ""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name == evolve_function_name:
                    evolved_function = ast.unparse(node)
                elif node.name == solve_function_name:
                    solve_function = ast.unparse(node)

        return (evolved_function, solve_function)
    # def start(
    #     self,
    #     spec: str,
    #     evolve_function_name: str,
    #     solve_function_name: str,
    #     inputs: Tuple[Any],
    # ):
    #     """Start the evolution process
    #
    #     This function creates the thread pools for the samplers, evaluators, and correctors, and starts the infinite evolution process.
    #
    #     """
    #     self.spec = spec
    #     self.evolve_function, self.solve_function = self.__parse_spec(
    #         self.spec, evolve_function_name, solve_function_name
    #     )
    #
    #     # Spawn samplers
    #     self.samplers = ThreadPoolExecutor(max_workers=self.config.n_samplers)
    #     # Spawn correctors
    #     self.correctors = ThreadPoolExecutor(max_workers=self.config.n_correctors)
    #     # Spawn evaluators
    #     self.evaluators = ThreadPoolExecutor(max_workers=self.config.n_evaluators)
    #
    #     # Register base evolve function and score in all islands
    #     initial_score = self.evaluators.submit(
    #         self.evaluator.eval, self.spec, inputs, self.solve_function
    #     ).result()
    #     self.evolver.populate_islands(self.evolve_function, initial_score)
    #
    #     while True:
    #         sampler_futures = []
    #         corrector_futures = []
    #         evaluator_futures = []
    #         for i in range(self.config.n_samplers):
    #             prompt, island_id = self.__get_prompt_and_island_id()
    #             sampler_futures.append(
    #                 self.samplers.submit(
    #                     self.__sample,
    #                     np.random.choice(self.endpoints, 1)[0],
    #                     prompt,
    #                     self.__yield_weighted_model_name(self.config.samplers),
    #                 )
    #             )
    #         for future in concurrent.futures.as_completed(sampler_futures):
    #             sample = RegExParser.parse(future.result())
    #             if (
    #                 self.config.n_correctors
    #                 and self.config.correctors
    #                 and self.corrector_endpoints
    #             ):
    #                 corrector_futures.append(
    #                     self.correctors.submit(
    #                         self.__correct_sample,
    #                         np.random.choice(self.corrector_endpoints, 1)[0],
    #                         sample,
    #                         self.__yield_weighted_model_name(self.config.correctors),
    #                     )
    #                 )
    #
    #         if (
    #             self.config.n_correctors
    #             and self.config.correctors
    #             and self.corrector_endpoints
    #         ):
    #             for future in concurrent.futures.as_completed(corrector_futures):
    #                 sample = RegExParser.parse(future.result())
    #                 evaluator_futures.append(
    #                     # TODO: Modify spec to delete base evolve function and append sample. Also, modify rename function name in sample to solve_function_name
    #                     self.evaluators.submit(
    #                         self.evaluator.eval,
    #                         self.spec,
    #                         inputs,
    #                         solve_function_name,
    #                     )
    #                 )
    #         # Pass output of evaluator futures to evolver
    #         else:
    #             pass
    #
    #         for future in concurrent.futures.as_completed(corrector_futures):
    #             sample = RegExParser.parse(future.result())
    #             # Send for evaluation

    # def __correct_sample(self, endpoint: str, prompt: str, model: str) -> str:
    #     prompt_aug = f"Correct this code to the best of your ability. If the code is fine as is, simply output the code in a markdown code block.\n\n {prompt}"
    #     try:
    #         response = requests.post(
    #             endpoint,
    #             data=json.dumps(
    #                 {"prompt": prompt_aug, "model": model, "stream": False}
    #             ),
    #         )
    #         return response.json()["response"]
    #     except:
    #         # If correct failed, return original sample
    #         return prompt

    # def __sample(self, endpoint: str, prompt: str, model: str) -> str:
    #     try:
    #         response = requests.post(
    #             endpoint,
    #             data=json.dumps({"prompt": prompt, "model": model, "stream": False}),
    #         )
    #         return response.json()["response"]
    #     except:
    #         # If sample failed, return the base evolve function that was implemented in the spec
    #         return self.__parse_spec(
    #             self.spec, self.evolve_function, self.solve_function
    #         )[0]
