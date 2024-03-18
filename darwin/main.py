from darwin.configuration.configuration import EvolverConfig
from darwin.evolving.evolver import Evolver


class Darwin:
    def __init__(self, specification: str, configuration: EvolverConfig = EvolverConfig()) -> None:
        self.specification = specification
        self.configuration = configuration
        self.evolver = Evolver(config=configuration)

    def start_evolution(self) -> None:
        pass

