import numpy as np
import itertools
from networkx import enumerate_all_cliques, from_numpy_array

def solve(r: int, b: int, n: int) -> int:
    mat_red = np.zeros((n, n))
    mat_blue = np.zeros((n, n))
    # Populate matrix based on priority
    for i in range(n):
        for j in range(i, n):
            prio = priority(i, j)
            # prio = priority(mat_red + 2 * mat_blue, i, j)
            if prio[0] > prio[1]:
                mat_red[i, j] = 1
                mat_red[j, i] = 1
            else:
                mat_blue[i, j] = 1
                mat_blue[j, i] = 1

    # Check red cliques
    n1 = n2 = 0
    for i in enumerate_all_cliques(from_numpy_array(mat_red)):
        if n1 >= 1000000:
            break

        if len(i) >= r:
            n1 += 1

    for i in enumerate_all_cliques(from_numpy_array(mat_blue)):
        if n2 >= 1000000:
            break
        if len(i) >= b:
            n2 += 1

    return max(n1, n2)


def evaluate(r: int, b: int, n: int):
    cliques = solve(r, b, n)
    return -cliques if cliques else 1


def priority(from_vertex: int, to_vertex: int) -> tuple[int, int]:
    """
    In combinatorics, Ramsey's theorem, in one of its graph-theoretic forms, states that one will find monochromatic cliques in any edge labelling
    (with colours) of a sufficiently large complete graph. To demonstrate the theorem for two colours (say, blue and red), let r and s be any two positive integers.
    Ramsey's theorem states that there exists a least positive integer R(r, s) for which every blue-red edge colouring of the complete graph on R(r, s) vertices
    contains a blue clique on r vertices or a red clique on s vertices. (Here R(r, s) signifies an integer that depends on both r and s.)

    ### Args:
    from_vertex: The originating vertex of the edge
    to_vertex: The destination vertex of the edge

    Return: A tuple of 2 integers representing the priority of making the edge from 'from_vertex' to 'to_vertex' either red or blue. The first index represents the 
    priority for red while the second index represents the priority for blue. If the value of the first index is larger than the value at the second index, the edge
    will be made red. Likewise, if the value at the second index is larger than the value at the first index, the edge will be made blue.
    """
    return (0, 0)


