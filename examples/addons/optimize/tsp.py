#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
# test data: http://elib.zib.de/pub/mp-testdata/tsp/tsplib/tsp/
import random
from typing import cast
from ezdxf.addons import genetic_algorithm as ga
from ezdxf.math import Vec2

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

bayg29 = [
    (1150.0, 1760.0),
    (630.0, 1660.0),
    (40.0, 2090.0),
    (750.0, 1100.0),
    (750.0, 2030.0),
    (1030.0, 2070.0),
    (1650.0, 650.0),
    (1490.0, 1630.0),
    (790.0, 2260.0),
    (710.0, 1310.0),
    (840.0, 550.0),
    (1170.0, 2300.0),
    (970.0, 1340.0),
    (510.0, 700.0),
    (750.0, 900.0),
    (1280.0, 1200.0),
    (230.0, 590.0),
    (460.0, 860.0),
    (1040.0, 950.0),
    (590.0, 1390.0),
    (830.0, 1770.0),
    (490.0, 500.0),
    (1840.0, 1240.0),
    (1260.0, 1500.0),
    (1280.0, 790.0),
    (490.0, 2130.0),
    (1460.0, 1420.0),
    (1260.0, 1910.0),
    (360.0, 1980.0),
]


def sum_dist(points):
    points.append(points[0])
    return sum(p1.distance(p2) for p1, p2 in zip(points, points[1:]))


class TSPEvaluator(ga.Evaluator):
    """Traveling Salesmen Problem"""

    def __init__(self, data):
        self.cities = Vec2.list(data)

    def evaluate(self, dna: ga.DNA) -> float:
        # searching for shortest path
        return -sum_dist([self.cities[i] for i in dna])


def show_log(log, name: str):
    x = []
    y = []
    avg = []
    for index, entry in enumerate(log, start=1):
        x.append(index)
        y.append(abs(entry.fitness))
        avg.append(abs(entry.avg_fitness))
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.plot(x, avg)
    ax.set(xlabel="generation", ylabel="fitness", title=f"TSP: {name}")
    ax.grid()
    plt.show()


def show_result(data, order: ga.DNA, name):
    x = []
    y = []
    for city in order:
        x.append(data[city][0])
        y.append(data[city][1])
    fig, ax = plt.subplots()
    ax.scatter(x, y)
    x.append(x[0])
    y.append(y[0])
    ax.plot(x, y)
    ax.set(title=f"TSP: {name}")
    ax.grid()
    plt.show()


def feedback(optimizer: ga.GeneticOptimizer):
    print(
        f"gen: {optimizer.generation:4}, "
        f"stag: {optimizer.stagnation:4}, "
        f"fitness: {abs(optimizer.best_fitness):.3f}"
    )
    return False


# RandomSwapMutate (swapping cities randomly) is very bad for this kind of
# problem! Changing the order of cities in a local environment is much better:
# - SwapNeighborMutate()
# - ReverseMutate()
# - ScrambleMutate()

# seed = ... not found
# DNA strands = 300 (population)
# elitism = 30
# crossover_rate = 0.9, RankBasedSelection
# mutate_rate = 0.05, SwapNeighbor

BEST_OVERALL = 9074.147

ELITISM = 30


def main(data, seed):
    random.seed(seed)
    optimizer = ga.GeneticOptimizer(TSPEvaluator(data), 1000)
    optimizer.reset_fitness(-1e99)  # required for searching for shortest path
    optimizer.max_stagnation = 200
    optimizer.mate = ga.MateOrderedCX()
    optimizer.crossover_rate = 0.9
    optimizer.mutation = ga.NeighborSwapMutate()
    optimizer.mutation_rate = 0.05
    optimizer.selection = ga.TournamentSelection(2)

    # count >= elitism, stores the <count> overall best solutions
    optimizer.hall_of_fame.count = ELITISM
    # preserve <elitism> overall best solutions in each generation
    optimizer.elitism = ELITISM

    optimizer.add_dna(ga.UniqueIntDNA.n_random(300, length=len(data)))
    optimizer.execute(feedback, 2)

    print(
        f"GeneticOptimizer: {optimizer.generation} generations x {optimizer.dna_count} "
        f"DNA strands, best result:"
    )
    evaluator = cast(TSPEvaluator, optimizer.evaluator)
    best_dist = abs(evaluator.evaluate(optimizer.best_dna))
    percent = best_dist / BEST_OVERALL * 100
    print(f"Shortest path overall: {BEST_OVERALL:.3f}")
    print(f"Shortest path: {best_dist:.3f} ({percent:.1f}%)")
    print(optimizer.best_dna)
    name = f"bay29, dist={int(best_dist)} ({percent:.1f}%), seed={seed}"
    show_log(optimizer.log, name)
    show_result(data, optimizer.best_dna, name)


if __name__ == "__main__":
    for s in range(40, 50):
        main(bayg29, s)
