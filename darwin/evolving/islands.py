import numpy as np
from scipy.special import softmax

from darwin.evolving.samples import Sample
from darwin.evolving.clusters import Cluster


class Island:
    def __init__(
        self,
        max_version: int,
        cluster_temperature: float,
        cluster_temperature_period: int,
    ) -> None:
        self.max_version = max_version
        self.cluster_temperature = cluster_temperature
        self.cluster_temperature_period = cluster_temperature_period

        # Right now clusters are just indexed with one score, but we could indexx them
        # using a tuple of all the scores on all inputs.
        self.clusters: dict[int, Cluster] = {}
        self.num_programs: int = 0

    def register_sample(self, sample: Sample) -> None:
        score = sample.score
        if score not in self.clusters:
            self.clusters[score] = Cluster(sample=sample)
        else:
            self.clusters[score].register_sample(sample)

        self.num_programs += 1

    def get_sample(self) -> tuple[Sample, int]:
        scores = np.array(list(self.clusters.keys()))
        temperature = self.cluster_temperature * (
            1
            - (self.num_programs % self.cluster_temperature_period)
            / self.cluster_temperature_period
        )
        p = softmax(scores / temperature)

        versions = min(len(self.clusters), self.max_version)

        scores = np.random.choice(scores, size=versions, p=p)
        scores = np.sort(scores)

        implementations = [self.clusters[score].get_sample() for score in scores]
        return implementations[-1], len(implementations)
