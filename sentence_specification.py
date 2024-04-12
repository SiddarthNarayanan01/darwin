import itertools
import numpy as np


def check_valid_combination(sentence: np.ndarray, t: int, k: int) -> bool:
    """
    This checks if the sentence is valid by testing every combination of 3 words from the sentence
    for if there exists at least one index where all elements of the word are different.

    First it loops over the combinations:
        Then it loops over all the indices:
            Then it loops over each word in the k_group and checks one of the indices has
            all different elements.
    """

    if np.size(sentence, axis=0) < k:
        collection = [[word for word in sentence]]
    else:
        collection = itertools.combinations(sentence, k)

    for k_group in collection:
        for i in range(t):
            seen = set()
            for word in k_group:
                if word[i] in seen:
                    break
                seen.add(word[i])
            else:
                break
        else:
            return False
    return True


def block_strings(dictionary, priorities, sentence, chosen, t, k):
    """
    Loops over every word in the dictionary and, if its priority is not negative infinity
    checks if this word would be valid to add to the sentence. If it's not, update its priority
    to be negative infinity.
    """

    for i, word in enumerate(dictionary):
        if priorities[i] != -np.inf:
            updated_sentence = np.concatenate([sentence, chosen[np.newaxis]], axis=0)
            updated_sentence = np.concatenate(
                [updated_sentence, word[np.newaxis]], axis=0
            )

            if not check_valid_combination(updated_sentence, t, k):
                priorities[i] = -np.inf


def solve(t: int, b: int, k: int) -> np.ndarray:
    """Calls the priority function and builds the sentence greedily"""

    # Cartesian product of alphabet B t times: B^t
    dictionary = np.array(
        list(itertools.product(tuple(range(b)), repeat=t)), dtype=np.int32
    )

    # Getting all priority values for each word in the dictionary
    priorities = np.array([float(priority(tuple(word), t)) for word in dictionary])

    # Sentence is the output
    sentence = np.empty((0, t), dtype=np.int32)

    while np.any(priorities != -np.inf):
        index = np.argmax(priorities)
        chosen = dictionary[index]
        priorities[index] = -np.inf
        block_strings(dictionary, priorities, sentence, chosen, t, k)

        # In the other funsearch implementations, chosen[None] would have been used
        # But I think that notation is confusing, and this does the same thing.
        sentence = np.concatenate([sentence, chosen[np.newaxis]], axis=0)

    return sentence


# darwin.eval
def evaluate(t: int, b: int, k: int) -> int:
    sentence = solve(t, b, k)
    return np.size(sentence, axis=0)


# darwin.evolve
def priority(word: tuple[int, ...], t: int) -> float:
    """Returns the priority in which we want to add a word to the sentence"""
    return 0.0


if __name__ == "__main__":
    """DON'T FORGET TO PUT @funsearch.run and @funsearch.evolve decorators!"""
    print(evaluate(4, 3, 3))
    sent = np.array(
        [
            [0, 0, 1, 2],
            [0, 1, 2, 0],
            [0, 2, 0, 1],
            [1, 2, 1, 0],
            [1, 1, 0, 2],
            [1, 0, 2, 1],
            [2, 0, 0, 0],
            [2, 1, 1, 1],
            [2, 2, 2, 2],
        ]
    )
    print(check_valid_combination(sent, 4, 3))
