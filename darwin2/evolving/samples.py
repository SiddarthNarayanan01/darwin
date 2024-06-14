class Sample:
    def __init__(self, code: str, island_id: int, score: int = 0) -> None:
        self.score = score
        self.island_id = island_id
        self.code = code

    def __repr__(self) -> str:
        return f"Island {self.island_id} with score: {self.score}"
