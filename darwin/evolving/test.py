from darwin.evolving.evolver import Evolver
from darwin.configuration.configuration import EvolverConfig


def main():
    function = """
    def priority() -> float:
        return 0.0
    """
    test = Evolver(
        EvolverConfig,
    )


main()
