class Sample:
    def __init__(self, code: str, island_id: int, score: int = 0) -> None:
        self.score = score
        self.island_id = island_id
        self.code = code
