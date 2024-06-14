import ast
import json
import pickle
import time
from collections import deque
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Manager, Queue
from typing import Any, Deque, Dict, List, Tuple

import numpy as np
import requests
from darwin2.client.logger_v2 import Logger
from darwin2.configuration.ollama import OllamaConfig
from darwin2.evaluating.evaluator import Evaluator
from darwin2.evolving.evolver import Evolver
from darwin2.evolving.samples import Sample
from darwin2.postprocessing.parser import RegExParser
from groq import Groq


class GroqClient:
    def __init__(
        self,
        endpoints: List[str],
        config: OllamaConfig,
        database_save: str | None = None,
        corrector_endpoints: List[str] | None = None,
    ) -> None:
        self.endpoints = endpoints
        self.corrector_endpoints = corrector_endpoints or endpoints
        self.config = config
        self.evaluator = Evaluator()
        self.client = Groq(
            api_key="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",
        )

        if database_save:
            with open(database_save, "rb") as f:
                self.evolver = pickle.load(f)
        else:
            self.evolver = Evolver(config.evolve_config)

    def start(
        self,
        spec: str,
        evolve_function_name: str,
        solve_function_name: str,
        inputs: Tuple[Any, ...],
        log_base_path: str,
    ):
        self.log = Logger(base_path=log_base_path)
        """Start the evolution process

        This function creates the thread pools for the samplers, evaluators, and correctors, and starts the infinite evolution process.

        """
        self.spec = spec
        self.base_evolve_function, self.solve_function = self.__parse_spec(
            self.spec, evolve_function_name, solve_function_name
        )
        self.log.log_misc(
            f"Parsed base_evolve_function and solve_function\nBase Evolve Function:\n{self.base_evolve_function}\nSolve Function:\n{self.solve_function}"
        )

        # Spawn samplers
        self.samplers = ThreadPoolExecutor(max_workers=self.config.n_samplers)

        if self.config.n_correctors:
            # Spawn correctors
            self.correctors = ThreadPoolExecutor(max_workers=self.config.n_correctors)
        # Spawn evaluators
        self.evaluators = ProcessPoolExecutor(max_workers=self.config.n_evaluators)

        samples_queue: Deque[Sample] = deque()
        corrections_queue: Deque[Sample] = deque()

        # TODO: Change to deque if processpool really does not work
        scores_queue = Manager().Queue()

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
        self.log.log_misc(f"Scored base_evolve_function: {sample.score}")
        self.evolver.populate_islands(sample)

        # Start infinite evolution loop
        self.log.log_misc("Starting evolution loop")
        n_sample_tasks = 0
        try:
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
                    n_sample_tasks += 1

                # Pass sample to correctors if needed
                if samples_queue:
                    sample = samples_queue.popleft()
                    sample.code = RegExParser.parse(sample.code)
                    self.log.log_misc("Received sample")
                    # Must send to evaluators instead
                    self.evaluators.submit(
                        self.evaluator.eval,
                        scores_queue,
                        spec,
                        sample,
                        inputs,
                        solve_function_name,
                        evolve_function_name,
                    )
                    n_sample_tasks -= 1

                if not scores_queue.empty():
                    sample = scores_queue.get()
                    self.log.log_misc("Scored sample")
                    if (
                        sample.score == 0
                        and self.config.n_correctors > 0
                        and self.config.correctors
                    ):
                        self.correctors.submit(
                            self.__correct_sample,
                            corrections_queue,
                            np.random.choice(self.corrector_endpoints, 1)[0],
                            sample,
                            self.__yield_weighted_model_name(self.config.correctors),
                        )
                    elif sample.score != 0:
                        self.log.scored_sample(sample)
                        self.evolver.register_sample(sample, [sample.score])

                if corrections_queue:
                    correction = corrections_queue.popleft()
                    self.log.log_misc("Received corrected sample")
                    self.log.log_sample(correction)
                    self.evaluators.submit(
                        self.evaluator.eval,
                        scores_queue,
                        spec,
                        correction,
                        inputs,
                        solve_function_name,
                        evolve_function_name,
                    )

                time.sleep(0.01)
        except KeyboardInterrupt as e:
            self.evolver.save_database()
            self.log.log_misc("KeyboardInterrupt")
            exit()

    def __yield_weighted_model_name(self, model_distribution: Dict[str, float]) -> str:
        return np.random.choice(
            list(model_distribution.keys()), 1, p=list(model_distribution.values())
        )[0]

    def __sample(
        self, samples_queue: Deque[Sample], endpoint: str, sample: Sample, model: str
    ):
        response = (
            self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": sample.code,
                    }
                ],
                model="gemma-7b-it",
            )
            .choices[0]
            .message.content
        )
        samples_queue.append(Sample(response, sample.island_id))

    def __correct_sample(
        self,
        corrections_queue: Deque[Sample],
        endpoint: str,
        sample: Sample,
        model: str,
    ):
        prompt_aug = f"Correct this code to the best of your ability. Fix any module-specific code like calls to nonexistent functions, improper data types, etc. Do not modify the parameters that the main function defines. If the code is fine as is, simply output the code in a markdown code block.\n\n {sample.code}"
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
        prompt += "Generate an improved function. Format your response in markdown syntax with a python code block containing the improved function. Do not modify the function's parameters."
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
