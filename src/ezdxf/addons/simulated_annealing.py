#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List
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
        self.min_fitness: float = 0.0
        self.start_time: float = 0.0
        self.mutation_rate: float = 0.1
        self.evaluator: ga.Evaluator = evaluator
        self.temperature: Temperature = LinearTemperature(500)
        self.mutation: ga.Mutate = ga.NeighborSwapMutate()
        # best result:
        self.best_fitness: float = 0.0
        self.best_dna: ga.DNA = ga.BitDNA([])

    def execute(self, candidate: ga.DNA, steps: int):
        self.start_time = time.perf_counter()
        temperature = self.temperature.get(1.0)
        self.best_fitness = self.evaluator.evaluate(candidate)
        self.best_dna = candidate
        self.log.add(0.0, temperature, self.best_fitness)

        for k in range(steps):
            step = 1.0 - (k + 1) / steps  # linear decreasing: 1.0 -> 0.0
            temperature = self.temperature.get(step)
            dna_new = self.neighbor(self.best_dna, step)
            fitness_new = self.evaluator.evaluate(dna_new)
            if fitness_new < self.best_fitness:
                self.add_log(fitness_new, temperature)
                self.best_fitness = fitness_new
                self.best_dna = dna_new
            else:
                p = self.probability(
                    self.best_fitness, fitness_new, temperature
                )
                if random.random() < p:
                    self.add_log(fitness_new, temperature)
                    self.best_fitness = fitness_new
                    self.best_dna = dna_new

            if self.best_fitness < self.min_fitness:
                break

    def probability(self, f0: float, f1: float, temperature: float) -> float:
        if temperature > 0.0:
            return math.exp(-abs(f1 - f0) / temperature)
        return 0.0

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
