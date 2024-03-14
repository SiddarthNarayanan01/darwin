from lib.evolving.evolver import Evolver
from lib.configuration.configuration import DBConfig


def main():
    function = """
    def priority() -> float:
        return 0.0
    """
    test = Evolver(
        DBConfig,
    )


main()
