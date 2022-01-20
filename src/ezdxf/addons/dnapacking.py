#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

from typing import (
    List,
    Iterable,
    Sequence,
    Optional,
    Callable,
)
import array
import copy
import enum
import itertools
import random
import time
from .binpacking import AbstractPacker

__all__ = ["DNA", "GeneticDriver"]


class MutationType(enum.Enum):
    FLIP = enum.auto()
    SWAP = enum.auto()


def _to_list(values) -> List[float]:
    return array.array("f", values)  # type: ignore


class DNA:
    __slots__ = ("_length", "_data", "fitness")

    def __init__(self, length: int, value: float = 0.0):
        self._length = int(length)
        if 0.0 <= value <= 1.0:
            self._data: List[float] = _to_list(
                itertools.repeat(value, self._length)
            )
        else:
            raise ValueError("data value out of range")
        self.fitness: Optional[float] = None

    @classmethod
    def random(cls, length: int) -> "DNA":
        dna = cls(length)
        dna.reset(random.random() for _ in range(length))
        return dna

    def _check_valid_data(self):
        if len(self._data) != self._length:
            raise ValueError("invalid data count")
        if not all(0.0 <= v <= 1.0 for v in self._data):
            raise ValueError("data value out of range")

    def copy(self):
        return copy.deepcopy(self)

    def taint(self):
        self.fitness = None

    def __eq__(self, other):
        assert isinstance(other, DNA)
        return self._data == other._data

    def __str__(self):
        fitness = ", fitness=None"
        if fitness is None:
            fitness = ", fitness=None"
        else:
            fitness = f", fitness={self.fitness:.4f}"
        return f"{str([round(v, 4) for v in self._data])}{fitness}"

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        return self._data.__getitem__(item)

    def __iter__(self):
        return iter(self._data)

    def reset(self, values: Iterable[float]):
        self._data = _to_list(values)
        self._check_valid_data()
        self.taint()

    def mutate(self, rate: float, mutation_type=MutationType.FLIP):
        for index in range(self._length):
            if random.random() < rate:
                self.mutate_at(index, mutation_type)

    def mutate_at(self, index, mutation_type=MutationType.FLIP):
        if mutation_type == MutationType.FLIP:
            self._data[index] = 1.0 - self._data[index]  # flip pick location
        elif mutation_type == MutationType.SWAP:
            index_left = index - 1  # 0 <-> -1; first <-> last
            left = self._data[index_left]
            self._data[index_left] = self._data[index]
            self._data[index] = left
        self.taint()

    def replace_tail(self, part: Sequence) -> None:
        self._data[-len(part) :] = _to_list(part)
        self._check_valid_data()
        self.taint()


def recombine_dna(dna1: DNA, dna2: DNA, index: int) -> None:
    part1 = dna1[index:]
    part2 = dna2[index:]
    dna1.replace_tail(part2)
    dna2.replace_tail(part1)


#############################################################################
# Optimizing only the order for the pack algorithm was not efficient, the
# BIGGER_FIRST strategy beats every other attempt!
# - schematic_packer() can be removed
#
# Next approach, find the optimal subset of items for the BIGGER_FIRST strategy
# to fill all bins
# 1. If all items fit into the bins, its done.
# 2. If not all items fit into the bins: search for the optimal subset of
#    items with the highest fitness.


class GeneticDriver:
    def __init__(
        self,
        packer: AbstractPacker,
        max_generations: int,
    ):
        if packer.is_packed:
            raise ValueError("packer is already packed")
        if max_generations < 1:
            raise ValueError("max_generations < 1")
        # data:
        self._packer = packer
        self._required_dna_length = len(packer.items)
        self._dna_strands: List[DNA] = []

        # options:
        self._max_generations = int(max_generations)
        self._max_fitness: float = 1.0
        self._crossover_rate = 0.70
        self._mutation_rate = 0.001
        self.selection_always_include_best_dna = True
        self.mutation_type1 = MutationType.FLIP
        self.mutation_type2 = MutationType.FLIP

        # state of last (current) generation:
        self.generation: int = 0
        self.runtime: float = 0.0
        self.best_dna = DNA(0)
        self.best_fitness: float = 0.0
        self.best_packer = packer
        self.stagnation: int = 0  # generations without improvement

    @property
    def max_fitness(self) -> float:
        return self._max_fitness

    @max_fitness.setter
    def max_fitness(self, value: float) -> None:
        if value > 1.0 or value < 0.0:
            raise ValueError("max_fitness not in range [0, 1]")
        self._max_fitness = value

    @property
    def crossover_rate(self) -> float:
        return self._crossover_rate

    @crossover_rate.setter
    def crossover_rate(self, value: float) -> None:
        if value > 1.0 or value < 0.0:
            raise ValueError("crossover_rate not in range [0, 1]")
        self._crossover_rate = value

    @property
    def mutation_rate(self) -> float:
        return self._mutation_rate

    @mutation_rate.setter
    def mutation_rate(self, value: float) -> None:
        if value > 1.0 or value < 0.0:
            raise ValueError("mutation_rate not in range [0, 1]")
        self._mutation_rate = value

    @property
    def is_executed(self) -> bool:
        return bool(self.generation)

    def add_dna(self, dna: DNA):
        if not self.is_executed:
            if len(dna) != self._required_dna_length:
                raise ValueError(
                    f"invalid DNA length, requires {self._required_dna_length}"
                )
            self._dna_strands.append(dna)
        else:
            raise TypeError("already executed")

    def add_random_dna(self, count: int):
        for _ in range(count):
            self.add_dna(DNA.random(self._required_dna_length))

    def execute(
        self,
        feedback: Callable[["GeneticDriver"], bool] = None,
        interval: float = 1.0,
        max_time: float = 1e99,
    ) -> None:
        if self.is_executed:
            raise TypeError("can only run once")
        if not self._dna_strands:
            print("no DNA defined!")
        t0 = time.perf_counter()
        start_time = t0
        for self.generation in range(1, self._max_generations + 1):
            self._measure_fitness()
            if self.best_fitness >= self._max_fitness:
                break
            t1 = time.perf_counter()
            self.runtime = t1 - start_time
            if self.runtime > max_time:
                break
            if feedback and t1 - t0 > interval:
                if feedback(self):  # stop if feedback() returns True
                    break
                t0 = t1
            self._selection()

    def _measure_fitness(self):
        self.stagnation += 1
        for dna in self._dna_strands:
            if dna.fitness is not None:
                continue
            p0 = self._packer.copy()
            p0.schematic_pack(iter(dna))
            fill_ratio = p0.get_fill_ratio()
            dna.fitness = fill_ratio
            if fill_ratio > self.best_fitness:
                self.best_fitness = fill_ratio
                self.best_packer = p0
                self.best_dna = dna.copy()
                self.stagnation = 0

    def _selection(self):
        wheel = self._make_wheel()
        dna_strands: List[DNA] = []
        count = len(self._dna_strands)
        while len(dna_strands) < count:
            dna1, dna2 = wheel.pick(2)
            dna1 = dna1.copy()
            dna2 = dna2.copy()
            if random.random() < self._crossover_rate:
                location = random.randrange(0, self._required_dna_length)
                recombine_dna(dna1, dna2, location)

            mutation_rate = self._mutation_rate * self.stagnation
            dna1.mutate(mutation_rate, self.mutation_type1)
            dna2.mutate(mutation_rate, self.mutation_type2)
            dna_strands.append(dna1)
            dna_strands.append(dna2)
        self._dna_strands = dna_strands

    def _make_wheel(self):
        wheel = WheelOfFortune()
        dna_strands = self._dna_strands
        best_fitness = self.best_fitness
        has_best = False

        sum_fitness = sum(dna.fitness for dna in dna_strands)
        if sum_fitness == 0.0:
            sum_fitness = 1.0

        for dna in dna_strands:
            if dna.fitness == best_fitness:
                # DNA gets copied, comparing by "is" does not work!
                has_best = True
            wheel.add_dna(dna, dna.fitness / sum_fitness)

        if not has_best and self.selection_always_include_best_dna:
            wheel.add_dna(self.best_dna, best_fitness / sum_fitness)
        return wheel


class WheelOfFortune:
    def __init__(self):
        self._dna_strands: List[DNA] = []
        self._weights: List[float] = []

    def add_dna(self, item: DNA, weight: float):
        self._dna_strands.append(item)
        self._weights.append(weight)

    def pick(self, count: int) -> Iterable[DNA]:
        return random.choices(self._dna_strands, self._weights, k=count)
