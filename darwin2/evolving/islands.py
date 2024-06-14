import numpy as np
from scipy.special import softmax

from darwin2.evolving.samples import Sample
from darwin2.evolving.clusters import Cluster


class Island:
    def __init__(
        self,
        max_version: int,
        cluster_temperature: float,
        cluster_temperature_period: int,
        examples_per_prompt: int,
    ) -> None:
        self.max_version = max_version
        self.cluster_temperature = cluster_temperature
        self.cluster_temperature_period = cluster_temperature_period
        self.examples_per_prompt = examples_per_prompt

        # Right now clusters are just indexed with one score, but we could indexx them
        # using a tuple of all the scores on all inputs.
        self.clusters: dict[int, Cluster] = {}
        self.num_programs: int = 0

    def register_sample(self, sample: Sample) -> None:
        score = sample.score
        # TODO: Fix
        if score not in self.clusters:
            self.clusters[score] = Cluster(sample=sample)
        else:
            self.clusters[score].register_sample(sample)

        self.num_programs += 1

    def get_samples(self) -> list[Sample]:
        keys = np.array(list(self.clusters.keys()))
        # TODO: Fix
        temperature = self.cluster_temperature * (
            1
            - (self.num_programs % self.cluster_temperature_period)
            / self.cluster_temperature_period
        )
        p = softmax(keys / temperature)
        with open("logs/probs.txt", "a") as f:
            f.write(f"Keys: {keys}\nProb: {p}\n")

        n_examples = min(len(self.clusters), self.examples_per_prompt)
        keys = np.random.choice(keys, size=n_examples, p=p)
        keys = np.sort(keys)

        implementations = [self.clusters[key].get_sample() for key in keys]
        return implementations
