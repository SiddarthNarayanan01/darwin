import time
import numpy as np
import scipy.special.softmax as softmax

# All the config stuff should be made in the config file
from funsearch.configuration import DBConfig

class Sample:
    pass


class Cluster:
    pass


class Island:
    pass


class Evolver:
    def __init__(
        self, 
        config: DBConfig,
        function_to_evolve: str
        ) -> None:

        self.config: DBConfig = config
        self.islands: list[Island] = []
        
        for _ in range(self.config.num_islands):
            self.islands.append(
                Island(
                    ...
                )
            )

        self.best_island_scores: list[float] = [-float('inf')] * config.num_islands
        self.worst_island_scores: list[float] = [-float('inf')] * config.num_islands

        self.best_islands: list[Sample | None] = [None] * config.num_islands
        self.worst_islands: list[Sample | None] = [None] * config.num_islands

        self.last_reset = time.time()
        self.migration_counter = 0

    def get_sample(self) -> Sample:
        island_id = np.random.randint(config.num_islands)
        chosen: Sample = self.islands[island_id]
        return chosen

    def register_sample(
        self,
        program: Sample,
        scores: list[int]
        island_id: int
        ) -> None:

        # I'm just reducing the scores to equal the last score, we could handle this better
        # in the future if we wanna be able to handle multiple inputs
        # i.e. [(7,3,3), (6,3,3), (5,3,3)] - For Trifference Problem
        score = scores[-1]

        change: bool = False
        change_score: list[float]
        change_program: list[Sample | None]
        self.islands[island_id].register_sample(sample, scores)

        # I do this to decide whether to change the worst/best score on the island easily if necessary
        if score > self.best_island_scores[island_id]:
            change_score = self.best_island_scores
            change_program = self.best_islands
            change = True
        else if score < self.worst_island_scores[island_id]:
            change_score = self.worst_island_scores
            change_program = self.worst_islands
            change = True

        if change:
            change_score[island_id] = score
            change_program[island_id] = program
            # Maybe we can log when a new best/worst score gets added?
        else:
            self.migration_counter += 1

        if self.migration_counter >= self.config.migration_rate:
            self.migrate_islands()

        if time.time() - self.last_reset > self.config.island_duration:
            self.last_reset = time.time()
            self.reset_islands()

    def reset_islands() -> None:
        """Doing the same as the funsearch paper, reseting the worst half of the islands"""

    def migrate_islands() -> None:
        """Migrating the worst member of an island to a different island"""


if __name__ == '__main__':
    db = Evolver(1, 2, 3, Island(), Island())
    print(db)
