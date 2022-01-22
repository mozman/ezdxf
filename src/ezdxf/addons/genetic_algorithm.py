#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

from typing import (
    List,
    Iterable,
    Optional,
    Callable,
    Type,
)
import abc
import copy
from dataclasses import dataclass
import enum
import random
import time
from .binpacking import AbstractPacker, pack_item_subset

__all__ = ["DNA", "Selection", "FloatDNA", "RouletteSelection",
    "GeneticOptimizer"]


class MutationType(enum.Enum):
    FLIP = enum.auto()
    SWAP = enum.auto()


class DNA(abc.ABC):
    fitness: Optional[float] = None
    _data: List

    @classmethod
    @abc.abstractmethod
    def random(cls, length):
        ...

    @abc.abstractmethod
    def reset(self, values: Iterable):
        ...

    def copy(self):
        return copy.deepcopy(self)

    def _taint(self):
        self.fitness = None

    def __eq__(self, other):
        assert isinstance(other, self.__class__)
        return self._data == other._data

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        return self._data.__getitem__(item)

    def __setitem__(self, key, value):
        self._data.__setitem__(key, value)
        self._taint()

    def __iter__(self):
        return iter(self._data)

    def mutate(self, rate: float, mutation_type=MutationType.FLIP):
        for index in range(len(self)):
            if random.random() < rate:
                self._taint()
                if mutation_type == MutationType.FLIP:
                    self.flip_mutate_at(index)
                elif mutation_type == MutationType.SWAP:
                    self.swap_mutate(index, index - 1)
                else:
                    raise TypeError(mutation_type)

    @abc.abstractmethod
    def flip_mutate_at(self, index: int) -> None:
        ...

    def swap_mutate(self, i1: int, i2: int) -> None:
        tmp = self._data[i2]
        self._data[i2] = self._data[i1]
        self._data[i1] = tmp


def recombine_dna_1pcx(dna1: DNA, dna2: DNA, index: int) -> None:
    """Single point crossover."""
    recombine_dna_2pcx(dna1, dna2, index, len(dna1))


def recombine_dna_2pcx(dna1: DNA, dna2: DNA, i1: int, i2: int) -> None:
    """Two point crossover."""
    part1 = dna1[i1:i2]
    part2 = dna2[i1:i2]
    dna1[i1:i2] = part2
    dna2[i1:i2] = part1


class FloatDNA(DNA):
    __slots__ = ("_data", "fitness")

    def __init__(self, values: Iterable[float]):
        self._data: List[float] = list(values)
        self._check_valid_data()
        self.fitness: Optional[float] = None

    @classmethod
    def random(cls, length: int) -> "FloatDNA":
        return cls(random.random() for _ in range(length))

    def _check_valid_data(self):
        if not all(0.0 <= v <= 1.0 for v in self._data):
            raise ValueError("data value out of range")

    def __str__(self):
        if self.fitness is None:
            fitness = ", fitness=None"
        else:
            fitness = f", fitness={self.fitness:.4f}"
        return f"{str([round(v, 4) for v in self._data])}{fitness}"

    def reset(self, values: Iterable[float]):
        self._data = list(values)
        self._check_valid_data()
        self._taint()

    def flip_mutate_at(self, index: int) -> None:
        self._data[index] = 1.0 - self._data[index]  # flip pick location


class BitDNA(DNA):
    __slots__ = ("_data", "fitness")

    def __init__(self, values: Iterable):
        self._data: List[bool] = list(bool(v) for v in values)
        self.fitness: Optional[float] = None

    @classmethod
    def random(cls, length: int) -> "BitDNA":
        return cls(bool(random.randint(0, 1)) for _ in range(length))

    def __str__(self):
        if self.fitness is None:
            fitness = ", fitness=None"
        else:
            fitness = f", fitness={self.fitness:.4f}"
        return f"{str([int(v) for v in self._data])}{fitness}"

    def reset(self, values: Iterable) -> None:
        self._data = list(bool(v) for v in values)
        self._taint()

    def flip_mutate_at(self, index: int) -> None:
        self._data[index] = not self._data[index]


class Selection(abc.ABC):
    @abc.abstractmethod
    def pick(self, count: int) -> Iterable[DNA]:
        ...

    @abc.abstractmethod
    def reset(self, strands: Iterable[DNA]):
        ...


TEvaluator = Callable[[AbstractPacker, DNA], float]


def subset_evaluator(packer: AbstractPacker, dna: DNA) -> float:
    pack_item_subset(packer, dna)
    return packer.get_fill_ratio()


@dataclass
class LogEntry:
    fitness: float
    avg_fitness: float


class GeneticOptimizer:
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
        self.name = "GeneticOptimizer"
        self.log: List[LogEntry] = []
        self._packer = packer
        self._required_dna_length = len(packer.items)
        self._dna_strands: List[DNA] = []

        # core components:
        self._dna_type: Type[DNA] = BitDNA
        self._selection: Selection = RouletteSelection()
        self._evaluator: TEvaluator = subset_evaluator

        # options:
        self.max_generations = int(max_generations)
        self.max_stagnation = 100
        self.max_fitness: float = 1.0
        self.max_time: float = 1e99
        self.crossover_rate = 0.70
        self.mutation_rate = 0.001
        self.elitism: int = 2
        self.mutation_type1 = MutationType.FLIP
        self.mutation_type2 = MutationType.FLIP

        # state of last (current) generation:
        self.generation: int = 0
        self.runtime: float = 0.0
        self.best_dna = BitDNA([])
        self.best_fitness: float = 0.0
        self.best_packer = packer
        self.stagnation: int = 0  # generations without improvement

    def set_dna_type(self, dna_type: Type[DNA]) -> None:
        self._dna_type = dna_type

    def set_selection(self, selection: Selection) -> None:
        self._selection = selection

    def set_evaluator(self, evaluator: TEvaluator) -> None:
        self._evaluator = evaluator

    @property
    def is_executed(self) -> bool:
        return bool(self.generation)

    @property
    def dna_count(self) -> int:
        return len(self._dna_strands)

    def add_random_dna(self, count: int):
        if not self.is_executed:
            self._dna_strands.extend(
                self._dna_type.random(self._required_dna_length)
                for _ in range(count)
            )
        else:
            raise TypeError("already executed")

    def execute(
        self,
        feedback: Callable[["GeneticOptimizer"], bool] = None,
        interval: float = 1.0,
    ) -> None:
        if self.is_executed:
            raise TypeError("can only run once")
        if not self._dna_strands:
            print("no DNA defined!")
        t0 = time.perf_counter()
        start_time = t0
        for self.generation in range(1, self.max_generations + 1):
            self.measure_fitness()
            t1 = time.perf_counter()
            self.runtime = t1 - start_time
            if (
                self.best_fitness >= self.max_fitness
                or self.runtime >= self.max_time
                or self.stagnation >= self.max_stagnation
            ):
                break
            if feedback and t1 - t0 > interval:
                if feedback(self):  # stop if feedback() returns True
                    break
                t0 = t1
            self.next_generation()

    def measure_fitness(self) -> None:
        self.stagnation += 1
        fitness_sum: float = 0.0
        for dna in self._dna_strands:
            if dna.fitness is not None:
                fitness_sum += dna.fitness
                continue
            p0 = self._packer.copy()
            fill_ratio = self._evaluator(p0, dna)
            dna.fitness = fill_ratio
            fitness_sum += fill_ratio
            if fill_ratio > self.best_fitness:
                self.best_fitness = fill_ratio
                self.best_packer = p0
                self.best_dna = dna.copy()
                self.stagnation = 0

        avg_fitness = 0.0
        count = len(self._dna_strands)
        if count > 0:
            avg_fitness = fitness_sum / count
        self.log.append(LogEntry(self.best_fitness, avg_fitness))

    def next_generation(self) -> None:
        selector = self._selection
        selector.reset(self._dna_strands)
        dna_strands: List[DNA] = []
        count = len(self._dna_strands)

        if self.elitism > 0:
            dna_strands.extend([self.best_dna] * self.elitism)

        while len(dna_strands) < count:
            dna1, dna2 = selector.pick(2)
            dna1 = dna1.copy()
            dna2 = dna2.copy()
            if random.random() < self.crossover_rate:
                self.recombination(dna1, dna2)
            self.mutation(dna1, dna2)
            dna_strands.append(dna1)
            dna_strands.append(dna2)
        self._dna_strands = dna_strands

    def recombination(self, dna1: DNA, dna2: DNA):
        i1 = random.randrange(0, self._required_dna_length)
        i2 = random.randrange(0, self._required_dna_length)
        if i1 > i2:
            i1, i2 = i2, i1
        recombine_dna_2pcx(dna1, dna2, i1, i2)

    def mutation(self, dna1: DNA, dna2: DNA):
        mutation_rate = self.mutation_rate * self.stagnation
        dna1.mutate(mutation_rate, self.mutation_type1)
        dna2.mutate(mutation_rate, self.mutation_type2)


class RouletteSelection(Selection):
    def __init__(self):
        self._strands: List[DNA] = []
        self._weights: List[float] = []

    def reset(self, strands: Iterable[DNA]):
        # dna.fitness is not None here!
        self._strands = list(strands)
        sum_fitness = sum(dna.fitness for dna in self._strands)
        if sum_fitness == 0.0:
            sum_fitness = 1.0
        self._weights = [dna.fitness / sum_fitness for dna in self._strands]  # type: ignore

    def pick(self, count: int) -> Iterable[DNA]:
        return random.choices(self._strands, self._weights, k=count)
