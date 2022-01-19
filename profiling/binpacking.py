#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import math
import random
import time

import ezdxf.addons.binpacking as bp


def make_sample(n: int, max_width: float, max_height: float, max_depth: float):
    for _ in range(n):
        yield random.random() * max_width, random.random() * max_height, random.random() * max_depth


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
    total_area = sum(item.get_volume() for item in packer.items)
    w = round(math.sqrt(total_area) / 2.0)
    h = w * 1.60
    packer.add_bin("bin", w, h)
    return packer


def setup_3d_packer(n: int) -> bp.Packer:
    items = make_sample(n, 20, 20, 20)
    packer = make_3d_packer(
        ((round(w) + 1, round(h) + 1, round(d) + 1) for w, h, d in items)
    )
    total_area = sum(item.get_volume() for item in packer.items)
    s = round(math.pow(total_area, 0.3))
    packer.add_bin("bin", s, s, s)
    return packer


def profile_bigger_first(packer: bp.AbstractPacker, strategy):
    t0 = time.perf_counter()
    packer.pack(strategy)
    t1 = time.perf_counter()
    return t1 - t0


def print_result(p0: bp.AbstractPacker, t: float):
    box = p0.bins[0]
    print(
        f"Packed {len(box.items)} items in {t:.3f}s, ratio: {p0.bins[0].get_fill_ratio():.3f}"
    )


ROUNDS = 10


def main(packer: bp.AbstractPacker):
    def feedback(driver: bp.GeneticDriver):
        print(
            f"generation: {driver.generation}, best fitness: {driver.best_fitness:.3f}"
        )
        return False

    print(packer.bins[0])
    print(f"Total item count: {len(packer.items)}")
    print("Bigger First Strategy:")
    p0 = packer.copy()
    strategy = bp.PickStrategy.BIGGER_FIRST
    t = profile_bigger_first(p0, strategy)
    print_result(p0, t)

    n_shuffle = 100
    t0 = time.perf_counter()
    p0 = bp.shuffle_pack(packer, n_shuffle)
    t1 = time.perf_counter()
    print(f"Shuffle {n_shuffle}x, best result:")
    print_result(p0, t1 - t0)

    n_generations = 200
    n_dns_strands = 50
    gd = bp.GeneticDriver(
        packer, max_generations=n_generations, max_fitness=1.0
    )
    gd.add_random_dna(n_dns_strands)
    gd.execute(feedback, interval=10.0)
    print(
        f"GeneticDriver: {n_generations} generations x {n_dns_strands} DNS strands, best result:"
    )
    print_result(gd.best_packer, gd.runtime)


if __name__ == "__main__":
    packer = setup_3d_packer(50)
    # packer = setup_flat_packer(50)
    main(packer)
