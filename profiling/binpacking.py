#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
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

import json

import ezdxf.addons.binpacking as bp
import ezdxf.addons.dnapacking as dp

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


def make_subset_driver(
    packer: bp.AbstractPacker, generations: int, dna_count: int
):
    driver = dp.GeneticDriver(packer, generations)
    driver.set_dna_type(dp.BitDNA)
    driver.set_evaluator(dp.subset_evaluator)
    driver.name = "pack item subset"
    driver.mutation_type1 = dp.MutationType.FLIP
    driver.mutation_type2 = dp.MutationType.FLIP
    driver.add_random_dna(dna_count)
    return driver


def run_genetic_driver(driver: dp.GeneticDriver):
    def feedback(driver: dp.GeneticDriver):
        print(
            f"gen: {driver.generation:4}, "
            f"stag: {driver.stagnation:4}, "
            f"fitness: {driver.best_fitness:.3f}"
        )
        return False

    print(
        f"\nGenetic algorithm search: {driver.name}\n"
        f"max generations={driver.max_generations}, DNA count={driver.dna_count}"
    )
    driver.execute(feedback, interval=3.0)
    print(
        f"GeneticDriver: {driver.generation} generations x {driver.dna_count} "
        f"DNA strands, best result:"
    )
    print_result(driver.best_packer, driver.runtime)


def dump_log(log, filename):
    data = [(e.runtime, e.fitness) for e in log]
    with open(filename, "wt") as fp:
        json.dump(data, fp, indent=4)


def show_log(log):
    x = []
    y = []
    moving_avg = []
    for index, entry in enumerate(log, start=1):
        x.append(index)
        y.append(entry.fitness)
        moving_avg.append(sum(y) / len(y))
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.plot(x, moving_avg)
    ax.set(
        xlabel="generation",
        ylabel="fitness",
        title="Strategy: pack item subset",
    )
    ax.grid()
    plt.show()


def load_log(filename):
    with open(filename, "rt") as fp:
        data = json.load(fp)
    return [dp.LogEntry(t, f) for t, f in data]


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

if __name__ == "__main__":
    args = parse_args()
    if args.view and plt and os.path.exists(DATA_LOG):
        log = load_log(DATA_LOG)
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
    driver = make_subset_driver(packer, args.generations, args.dna)
    run_genetic_driver(driver)
    dump_log(driver.log, DATA_LOG)
    if plt is not None:
        show_log(driver.log)
