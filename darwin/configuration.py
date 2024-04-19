from darwin.sampling.backend import BackendType
from typing import Dict, List

from darwin.sampling.models import ModelType


class EvolverConfig:
    def __init__(
        self,
        num_islands: int = 10,
        reset_period: int = 60 * 60 * 4,
        proportion_to_reset: float = 0.5,
        migration_rate: int = 10,
        max_versions: int = 5,
        init_temperature: float = 0.1,
        temperature_period: int = 200,
        examples_per_prompt: int = 2,
    ) -> None:
        self.num_islands: int = num_islands
        self.reset_period: int = reset_period
        self.proportion_to_reset: float = proportion_to_reset
        self.migration_rate: int = migration_rate
        self.max_versions: int = max_versions
        self.init_temperature: float = init_temperature
        self.temperature_period: int = temperature_period
        self.examples_per_prompt: int = examples_per_prompt


class SampleConfig:
    def __init__(
        self,
        model_distribution: Dict[ModelType, float],
        backend: BackendType = BackendType.llamacpp,
        n_samplers: int = 4,
        **kwargs,
    ) -> None:
        if len(model_distribution) > n_samplers:
            raise ValueError("Number of models cannot exceed number of samplers.")

        if (
            sum(
                [
                    int(round(model_distribution[i], 2) * 100)
                    for i in model_distribution.keys()
                ]
            )
            != 100
        ):
            raise ValueError(
                "Ensure that the percentages in model_distribution add to 1"
            )

        # self.models = models
        self.model_distribution = model_distribution
        self.backend = backend
        if backend == BackendType.ollama:
            if "ollama_server_address" not in kwargs:
                raise ValueError(
                    "Ollama backend provided but no ollama_server_address found. Please specify the ollama_server_address (e.g., http://localhost:11434)"
                )
        self.n_samplers = n_samplers


class PostProcessConfig:
    def __init__(
        self,
        n_postprocessors=4,
        correct_samples=False,
        model_distribution: Dict[ModelType, float] | None = None,
    ) -> None:
        self.n_postprocessors = n_postprocessors
        if correct_samples and not model_distribution:
            raise ValueError(
                "correct_samples = True but no model_distribution provided. Please provide the models and their percentage of total models that will be used to correct the samples"
            )

        if model_distribution and len(model_distribution) > n_postprocessors:
            raise ValueError("Number of models cannot exceed number of samplers.")
        if model_distribution and (
            sum(
                [
                    int(round(model_distribution[i], 2) * 100)
                    for i in model_distribution.keys()
                ]
            )
            != 100
        ):
            raise ValueError(
                "Ensure that the percentages in model_distribution add to 1"
            )
        self.model_distribution = model_distribution


class EvaluationConfig:
    def __init__(self, n_evaluators: int = 8, sanbox: bool = False) -> None:
        self.n_evaluators = n_evaluators
        self.sandbox = sanbox


class SpecParseConfig:
    def __init__(self, evolved_function_name: str, solver_function_name: str):
        self.evolved_function_name = evolved_function_name
        self.solver_function_name = solver_function_name


class DarwinConfig:
    def __init__(
        self,
        sample_config: SampleConfig,
        spec_parse_config: SpecParseConfig,
        postprocess_config: PostProcessConfig | None = None,
        evaluation_config: EvaluationConfig | None = None,
        evolve_config: EvolverConfig | None = None,
    ) -> None:
        self.parse = spec_parse_config
        self.sample = sample_config
        self.postprocess = postprocess_config or PostProcessConfig()
        self.eval = evaluation_config or EvaluationConfig()
        self.evolve = evolve_config or EvolverConfig()
