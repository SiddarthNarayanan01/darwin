import numpy as np
from scipy.special import softmax

from lib.evolving.samples import Sample


class Cluster:
    def __init__(self, sample: Sample) -> None:
        self.score: int = sample.score
        self.samples: list[Sample] = sample
        self.lengths: list[int] = [len(sample.program)]

    def register_sample(self, sample: Sample) -> None:
        self.samples.append(sample)
        self.lengths.append(len(sample.program))

    def get_sample(self) -> Sample:
        normalized = (np.array(self.lengths) - min(self.lengths)) / (
            max(self.lengths) + 1e-6
        )
        return np.random.choice(self.samples, p=softmax(-normalized))
