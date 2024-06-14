from typing import Tuple
import time
import numpy as np
from scipy.special import softmax
import random
import pickle

from darwin2.evolving.islands import Island
from darwin2.evolving.samples import Sample

# All the config stuff should be made in the config file
from darwin2.configuration.evolve import EvolveConfig


class Evolver:
    def __init__(self, config: EvolveConfig) -> None:
        self.config: EvolveConfig = config
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

    def populate_islands(self, sample: Sample):
        for id in range(self.config.num_islands):
            self.register_sample(Sample(sample.code, id, sample.score), [sample.score])

    def get_samples(self) -> Tuple[list[str], int]:
        island_id = random.choice(list(self.active_islands_ids))
        samples = self.islands[island_id].get_samples()
        return [s.code for s in samples], island_id

    # TODO: create alternative register_sample function that registers function
    # into random island
    def register_sample(
        self,
        sample: Sample,
        scores: list[int],
    ) -> None:
        # I'm just reducing the scores to equal the last score, we could handle this better
        # in the future if we wanna be able to handle multiple inputs
        # i.e. [(7,3,3), (6,3,3), (5,3,3)] - For Trifference Problem
        score = scores[-1]

        self.islands[sample.island_id].register_sample(sample)
        self.active_islands_ids.add(sample.island_id)

        # I do this to decide whether to change the worst/best score on the island easily if necessary
        if (
            self.best_sample_per_island[sample.island_id] is None
            or score > self.best_sample_per_island[sample.island_id].score  # type: ignore
        ):
            self.best_sample_per_island[sample.island_id] = sample
            self.migration_counter_per_island[sample.island_id] = 0
        elif (
            self.worst_sample_per_island[sample.island_id] is None
            or score < self.worst_sample_per_island[sample.island_id].score  # type: ignore
        ):
            self.worst_sample_per_island[sample.island_id] = sample
            self.migration_counter_per_island[sample.island_id] += 1
        else:
            self.migration_counter_per_island[sample.island_id] += 1

        if (
            self.migration_counter_per_island[sample.island_id]
            >= self.config.migration_rate
        ):
            self.migration_counter_per_island[sample.island_id] = 0
            self.migrate_islands(sample.island_id)

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
            self.register_sample(
                Sample(founder.code, idx, founder.score), [founder.score]
            )

    def migrate_islands(self, from_island_id) -> None:
        """Migrating the worst member of an island to a different island"""
        best = np.array([i.score for i in self.best_sample_per_island])
        to_island_id = np.random.choice(self.islands, 1, p=softmax(-best))
        self.register_sample(
            self.worst_sample_per_island[from_island_id],
            [self.worst_sample_per_island[from_island_id].score],
        )
        self.migration_counter_per_island[from_island_id] = 0
        # delete from original island?

    def save_database(self):
        with open("logs/database.pickle", "wb") as f:
            pickle.dump(self, f)
