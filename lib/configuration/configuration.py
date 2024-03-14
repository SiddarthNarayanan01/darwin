class DBConfig:
    num_islands: int = 10
    reset_period: int = 60 * 60 * 4  # 4 Hours
    migration_rate: int = 10
    max_versions: int = 5
    init_temperature: float = 0.1
    temperature_period: int = 200  # We can play around with this number, google had it at 30000 but that seems like a lot for us lol
