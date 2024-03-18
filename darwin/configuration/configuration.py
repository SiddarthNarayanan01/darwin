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
    ) -> None:
        self.num_islands: int = num_islands
        self.reset_period: int = reset_period
        self.proportion_to_reset: float = proportion_to_reset
        self.migration_rate: int = migration_rate
        self.max_versions: int = max_versions
        self.init_temperature: float = init_temperature
        self.temperature_period: int = temperature_period

class InferenceConfig:
    pass

class VerificationConfig:
    pass

class DarwinConfig:
    pass
