#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import cast

import math
import random
import os
import time
import sys
import argparse

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

import ezdxf.addons.binpacking as bp
import ezdxf.addons.genetic_algorithm as ga

SEED = 47856535


def make_sample(n: int, max_width: float, max_height: float, max_depth: float):
    for _ in range(n):
        yield (
            random.random() * max_width,
            random.random() * max_height,
            random.random() * max_depth,
        )


def make_flat_packer(items) -> bp.FlatPacker:
    packer = bp.FlatPacker()
    for index, (w, h) in enumerate(items):
        packer.add_item(str(index), w, h)
    return packer


def make_3d_packer(items) -> bp.Packer:
    packer = bp.Packer()
    for index, (w, h, d) in enumerate(items):
        packer.add_item(str(index), w, h, d)
    return packer


def setup_flat_packer(n: int) -> bp.FlatPacker:
    items = make_sample(n, 20, 20, 20)
    packer = make_flat_packer(
        ((round(w) + 1, round(h) + 1) for w, h, d in items)
    )
    area = packer.get_unfitted_volume()
    w = round(math.sqrt(area) / 2.0)
    h = w * 1.60
    packer.add_bin("bin", w, h)
    return packer


def setup_3d_packer(n: int) -> bp.Packer:
    items = make_sample(n, 20, 20, 20)
    packer = make_3d_packer(
        ((round(w) + 1, round(h) + 1, round(d) + 1) for w, h, d in items)
    )
    volume = packer.get_unfitted_volume()
    s = round(math.pow(volume, 1.0 / 3.1))
    packer.add_bin("bin", s, s, s)
    return packer


def print_result(p0: bp.AbstractPacker, t: float):
    box = p0.bins[0]
    print(
        f"Packed {len(box.items)} items in {t:.3f}s, "
        f"ratio: {p0.get_fill_ratio():.3f}"
    )


def run_bigger_first(packer: bp.AbstractPacker):
    print("\nBigger first strategy:")
    p0 = packer.copy()
    strategy = bp.PickStrategy.BIGGER_FIRST
    t0 = time.perf_counter()
    p0.pack(strategy)
    t1 = time.perf_counter()
    print_result(p0, t1 - t0)


def run_shuffle(packer: bp.AbstractPacker, shuffle_count: int):
    print("\nShuffle strategy:")
    n_shuffle = shuffle_count
    t0 = time.perf_counter()
    p0 = bp.shuffle_pack(packer, n_shuffle)
    t1 = time.perf_counter()
    print(f"Shuffle {n_shuffle}x, best result:")
    print_result(p0, t1 - t0)


def make_subset_optimizer(
    packer: bp.AbstractPacker, generations: int, dna_count: int
):
    evaluator = bp.SubSetEvaluator(packer)
    optimizer = ga.GeneticOptimizer(evaluator, max_generations=generations)
    optimizer.name = "pack item subset"
    optimizer.add_dna(ga.BitDNA.n_random(dna_count, len(packer.items)))
    return optimizer


def run(optimizer: ga.GeneticOptimizer):
    def feedback(optimizer: ga.GeneticOptimizer):
        print(
            f"gen: {optimizer.generation:4}, "
            f"stag: {optimizer.stagnation:4}, "
            f"fitness: {optimizer.best_fitness:.3f}"
        )
        return False

    print(
        f"\nGenetic algorithm search: {optimizer.name}\n"
        f"max generations={optimizer.max_generations}, DNA count={optimizer.dna_count}"
    )
    optimizer.execute(feedback, interval=3.0)
    print(
        f"GeneticOptimizer: {optimizer.generation} generations x {optimizer.dna_count} "
        f"DNA strands, best result:"
    )
    evaluator = cast(bp.SubSetEvaluator, optimizer.evaluator)
    best_packer = evaluator.run_packer(optimizer.best_dna)
    print_result(best_packer, optimizer.runtime)


def show_log(log: ga.Log):
    x = []
    y = []
    avg = []
    for index, entry in enumerate(log.entries, start=1):
        x.append(index)
        y.append(entry.fitness)
        avg.append(entry.avg_fitness)
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.plot(x, avg)
    ax.set(
        xlabel="generation",
        ylabel="fitness",
        title="Strategy: pack item subset",
    )
    ax.grid()
    plt.show()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-g",
        "--generations",
        type=int,
        default=200,
        help="generation count",
    )
    parser.add_argument(
        "-d",
        "--dna",
        type=int,
        default=50,
        help="count of DNA strands",
    )
    parser.add_argument(
        "-i",
        "--items",
        type=int,
        default=50,
        help="items count",
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        default=SEED,
        help="random generator seed",
    )
    parser.add_argument(
        "-v",
        "--view",
        action="store_true",
        default=False,
        help="view logged data",
    )
    return parser.parse_args()


DATA_LOG = "binpacking.json"


def main():
    args = parse_args()
    if args.view and plt and os.path.exists(DATA_LOG):
        log = ga.Log.load(DATA_LOG)
        show_log(log)
        sys.exit()
    random.seed(args.seed)
    packer = setup_3d_packer(args.items)
    # packer = setup_flat_packer(50)
    print(packer.bins[0])
    print(f"Total item count: {len(packer.items)}")
    print(f"Total item volume: {packer.get_unfitted_volume():.3f}")
    print(f"Random Seed: {args.seed}")
    run_bigger_first(packer)
    optimizer = make_subset_optimizer(packer, args.generations, args.dna)
    run(optimizer)
    optimizer.log.dump(DATA_LOG)
    if plt is not None:
        show_log(optimizer.log)


if __name__ == "__main__":
    main()
