import time
import numpy as np
from scipy.special import softmax
import random

from darwin.evolving.islands import Island
from darwin.evolving.samples import Sample

# All the config stuff should be made in the config file
from darwin.configuration import EvolverConfig


class Evolver:
    def __init__(self, config: EvolverConfig) -> None:
        self.config: EvolverConfig = config
        self.islands: list[Island] = []
        self.active_islands_ids: set[int] = set()
        for _ in range(self.config.num_islands):
            self.islands.append(
                Island(
                    self.config.max_versions,
                    self.config.init_temperature,
                    self.config.temperature_period,
                    self.config.examples_per_prompt,
                )
            )

        self.best_sample_per_island: list[Sample | None] = [None] * config.num_islands
        self.worst_sample_per_island: list[Sample | None] = [None] * config.num_islands

        self.last_reset = time.time()
        self.migration_counter_per_island: list[int] = [0] * config.num_islands

    def populate_islands(self, function: str):
        for i in range(self.config.num_islands):
            self.register_sample(Sample(function), [0], i)

    def get_samples(self) -> list[Sample]:
        island_id = random.choice(list(self.active_islands_ids))
        samples = self.islands[island_id].get_samples()
        return samples

    # TODO: create alternative register_sample function that registers function
    # into random island
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
        self.active_islands_ids.add(island_id)

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
            self.migrate_islands(island_id)

        if time.time() - self.last_reset > self.config.reset_period:
            self.last_reset = time.time()
            self.reset_islands()

    def reset_islands(self) -> None:
        """Doing the same as the funsearch paper, reseting the worst half of the islands"""
        num_islands_to_reset = int(
            self.config.num_islands * (1 - self.config.proportion_to_reset)
        )
        sorted_island_indices = np.argsort(
            [x.score if x else -float("int") for x in self.best_sample_per_island]
        )
        kept_islands = sorted_island_indices[num_islands_to_reset:]
        reset_islands = sorted_island_indices[:num_islands_to_reset]

        for idx in reset_islands:
            self.active_islands_ids.remove(idx)
            self.islands[idx] = Island(
                self.config.max_versions,
                self.config.init_temperature,
                self.config.temperature_period,
                self.config.examples_per_prompt,
            )
            self.best_sample_per_island[idx] = None
            self.worst_sample_per_island[idx] = None
            founder_id = np.random.choice(kept_islands)
            founder = self.best_sample_per_island[founder_id]
            self.register_sample(founder, [founder.score], idx)

    def migrate_islands(self, from_island_id) -> None:
        """Migrating the worst member of an island to a different island"""
        best = np.array([i.score for i in self.best_sample_per_island])
        to_island_id = np.random.choice(self.islands, 1, p=softmax(-best))
        self.register_sample(
            self.worst_sample_per_island[from_island_id],
            [self.worst_sample_per_island[from_island_id].score],
            to_island_id,
        )
        self.migration_counter_per_island[from_island_id] = 0
        # delete from original island?
