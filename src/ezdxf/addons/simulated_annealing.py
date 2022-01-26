#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Callable
import abc
from dataclasses import dataclass
import math
import random
import time

from . import genetic_algorithm as ga


class Temperature(abc.ABC):
    @abc.abstractmethod
    def get(self, step: float) -> float:
        ...


class LinearTemperature(Temperature):
    def __init__(self, start: float):
        self.start = start

    def get(self, step: float) -> float:
        return self.start * step


class ExponentialTemperature(Temperature):
    def __init__(self, start: float, alpha: float):
        self.start = start
        self.alpha = alpha

    def get(self, step: float) -> float:
        return self.start * math.pow(step, self.alpha)


PFunction = Callable[[float, float, float], float]


def minimize(e0: float, e1: float, temperature: float) -> float:
    """Compute transition probability.

    Args:
        e0: current lowest energy state (best fitness)
        e1: new energy state
        temperature: system temperature

    """
    if e1 < e0:
        return 1.0
    if temperature > 0.0:
        return math.exp(-abs(e1 - e0) / temperature)
    return 0.0


class Log:
    @dataclass
    class Entry:
        runtime: float
        temperature: float
        fitness: float

    def __init__(self):
        self.entries: List[Log.Entry] = []

    def add(self, runtime: float, temperature: float, fitness: float) -> None:
        self.entries.append(
            Log.Entry(
                runtime=runtime,
                fitness=fitness,
                temperature=temperature,
            )
        )


class SimulatedAnnealing:
    """Simulated annealing (SA) is a probabilistic technique for approximating
    the global optimum of a given function.

    Source: https://en.wikipedia.org/wiki/Simulated_annealing

    """

    def __init__(self, evaluator: ga.Evaluator):
        self.log = Log()
        self.start_time: float = 0.0
        self.mutation_rate: float = 0.1
        self.stagnation: int = 0
        self.restart: int = 200
        self.evaluator: ga.Evaluator = evaluator
        self.temperature: Temperature = LinearTemperature(500)
        self.mutation: ga.Mutate = ga.NeighborSwapMutate()
        self.probability: PFunction = minimize
        self.best_fitness: float = 0.0
        self.best_dna: ga.DNA = ga.BitDNA([])

    def execute(self, candidate: ga.DNA, steps: int):
        self.start_time = time.perf_counter()
        self.best_fitness = self.evaluator.evaluate(candidate)
        self.best_dna = candidate
        self.log.add(0.0, self.temperature.get(1.0), self.best_fitness)
        current_fitness = self.best_fitness
        current_dna = candidate

        for k in range(steps):
            self.stagnation += 1
            step = 1.0 - (k + 1) / steps  # linear decreasing: 1.0 -> 0.0
            new_dna = self.neighbor(current_dna, step)
            new_fitness = self.evaluator.evaluate(new_dna)
            temperature = self.temperature.get(step)
            p = self.probability(current_fitness, new_fitness, temperature)
            if random.random() < p:
                self.stagnation = 0
                self.add_log(new_fitness, temperature)
                current_fitness = new_fitness
                current_dna = new_dna
                if new_fitness < self.best_fitness:
                    self.best_fitness = new_fitness
                    self.best_dna = new_dna

            if self.stagnation > self.restart:
                self.stagnation = 0
                current_dna = self.best_dna
                current_fitness = self.best_fitness

    def neighbor(self, candidate: ga.DNA, step: float) -> ga.DNA:
        candidate2 = candidate.copy()
        self.mutation.mutate(candidate2, step)
        return candidate2

    def add_log(self, fitness: float, temperature: float) -> None:
        self.log.add(
            time.perf_counter() - self.start_time,
            temperature,
            fitness,
        )
