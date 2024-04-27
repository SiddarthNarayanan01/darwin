from typing import Dict
from darwin2.configuration.evolve import EvolveConfig


class OllamaConfig:
    """Required OllamaClient configuration options.

    Configuration Options:

    samplers: Dict[str, float] (Required)
    - Represents the proportion of total samplers (n_samplers) for each model.
      The key should be the name of the model stored by ollama. Type `ollama list`
      to see all the downloaded models. Note, the proportions must add to 1.
      Example:
      samplers = {"llama3:7b": 0.5, "deepseek-coder:6.7b-instruct": 0.5}

    n_samplers: int = 4 (Default)
    - The total number of samplers for the evolution.

    n_correctors: int (Optional)
    - The total number of models used to correct the samples generated by the
      samplers. If None, samples will not be corrected for any programmatic
      issues.

    correctors: Dict[str, float] (Optional)
    - Represents the proportion of n_correctors for each correction model. The
      key should once again be the name of the model stored by ollama.

    n_evaluators: int = 10 (Default)
    - The total number of programs to evaluate the samples according to the provided
      evaluation function.

    evolve_config: EvolveConfig (Optional)
    - A bunch of evolution-related configuration options. If None, Darwin will use
      a base config that should work just fine.

    """

    def __init__(
        self,
        samplers: Dict[str, float],
        n_samplers: int = 4,
        n_correctors: int = 0,
        correctors: Dict[str, float] | None = None,
        n_evaluators: int = 10,
        evolve_config: EvolveConfig | None = None,
    ) -> None:
        # Argument checks

        if n_samplers <= 0:
            raise ValueError("Argument `n_samplers` must be positive")

        if not self.__distribution_sums_to_1(samplers):
            raise ValueError("Proportions in argument `samplers` must add to 1")

        if n_correctors < 0:
            raise ValueError("Argument `n_correctors` cannot be negative")

        if n_correctors > 0:
            if not correctors:
                raise ValueError(
                    "Argument `n_correctors` provided by argument `correctors` is missing. See help(OllamaConfig)"
                )
            elif not self.__distribution_sums_to_1(correctors):
                raise ValueError("Proportions in argument `correctors` must add to 1")

        if n_evaluators <= 0:
            raise ValueError("Argument `n_evaluators` must be positive")

        self.samplers = samplers
        self.n_samplers = n_samplers
        self.n_correctors = n_correctors
        self.correctors = correctors
        self.n_evaluators = n_evaluators
        self.evolve_config = evolve_config or EvolveConfig()

    def __distribution_sums_to_1(self, dist: Dict[str, float]) -> bool:
        # To avoid decimal imprecision errors. "private" method
        sum = 0
        for i in dist.values():
            # We allow three decimal places for the float
            sum += int(i * 1000)

        return sum == 1000