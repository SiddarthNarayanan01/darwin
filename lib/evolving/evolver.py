import time
import numpy as np
from scipy.special import softmax

# All the config stuff should be made in the config file
from lib.configuration.configuration import DBConfig


class Sample:
    score: int
    pass


class Cluster:
    pass


class Island:
    def register_sample(sample: Sample):
        pass


class Evolver:
    def __init__(self, config: DBConfig, function_to_evolve: str) -> None:
        self.config: DBConfig = config
        self.islands: list[Island] = []
        for _ in range(self.config.num_islands):
            self.islands.append(Island(...))

        self.best_sample_per_island: list[Sample | None] = [None] * config.num_islands
        self.worst_sample_per_island: list[Sample | None] = [None] * config.num_islands

        self.last_reset = time.time()
        self.migration_counter_per_island: list[int] = [0] * config.num_islands

    def get_sample(self) -> Sample:
        island_id = np.random.randint(self.config.num_islands)
        chosen: Sample = self.islands[island_id].get_sample()
        return chosen

    def register_sample(
        self,
        sample: Sample,
        scores: list[int],
        island_id: int,
    ) -> None:
        # I'm just reducing the scores to equal the last score, we could handle this better
        # in the future if we wanna be able to handle multiple inputs
        # i.e. [(7,3,3), (6,3,3), (5,3,3)] - For Trifference Problem
        score = scores[-1]

        self.islands[island_id].register_sample(sample)

        # I do this to decide whether to change the worst/best score on the island easily if necessary
        if score > self.best_sample_per_island[island_id].score:
            self.best_sample_per_island[island_id] = sample
            self.migration_counter_per_island[island_id] = 0
        elif score < self.worst_sample_per_island[island_id].score:
            self.worst_sample_per_island[island_id] = sample
            self.migration_counter_per_island[island_id] += 1
        else:
            self.migration_counter_per_island[island_id] += 1

        if self.migration_counter_per_island[island_id] >= self.config.migration_rate:
            self.migrate_islands()

        if time.time() - self.last_reset > self.config.island_duration:
            self.last_reset = time.time()
            self.reset_islands()

    def reset_islands(self) -> None:
        """Doing the same as the funsearch paper, reseting the worst half of the islands"""

    def migrate_islands(self, from_island_id) -> None:
        """Migrating the worst member of an island to a different island"""
        best = np.array([i.score for i in self.best_sample_per_island])
        to_island_id = np.random.choice(self.islands, 1, p=softmax(-best))
        self.register_sample(
            self.worst_sample_per_island[from_island_id],
            [self.worst_sample_per_island[from_island_id].score],
            to_island_id,
        )
        # delete from original island?
