#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Iterable, List, cast
import enum
import sys
import argparse

import ezdxf
from ezdxf.entities import DXFGraphic
from ezdxf.math import Matrix44, BoundingBox
from ezdxf.path import Path, make_path, nesting
from ezdxf.addons import binpacking as bp
from ezdxf.addons import genetic_algorithm as ga
from ezdxf import colors

DEBUG = True
GENERATIONS = 200
DNA_COUNT = 50


class Bundle:
    def __init__(self, entities: List[DXFGraphic], box: BoundingBox):
        self.entities = entities
        self.bounding_box = box

    def transform(self, m: Matrix44):
        self.bounding_box = BoundingBox(
            [
                m.transform(self.bounding_box.extmin),
                m.transform(self.bounding_box.extmax),
            ]
        )
        for e in self.entities:
            e.transform(m)

    def __str__(self):
        return ", ".join(str(e) for e in self.entities)

    def set_properties(self, layer: str, color: int):
        for e in self.entities:
            e.dxf.color = color
            e.dxf.layer = layer


def build_bundles(paths: Iterable[Path]) -> Iterable[Bundle]:
    def append_holes(holes):
        for hole in holes:
            if isinstance(hole, Path):
                # just for edge cases, in general:
                # holes should be inside of the contour!
                box.extend(hole.control_vertices())
                entities.append(hole.user_data)
            else:
                append_holes(hole)

    # the fast bbox detection algorithm is not very accurate!
    for polygon in nesting.fast_bbox_detection(paths):
        contour = polygon[0]
        box = BoundingBox(contour.control_vertices())
        # optional: add some spacing between items if required:
        box.grow(0.5)
        entities = [contour.user_data]
        for hole in polygon[1:]:
            append_holes(hole)
        yield Bundle(entities, box)


def run_optimizer(packer):
    def feedback(optimizer: ga.GeneticOptimizer):
        print(
            f"gen: {optimizer.generation:4}, "
            f"stag: {optimizer.stagnation:4}, "
            f"fitness: {optimizer.best_fitness:.3f}"
        )
        return False
    evaluator = bp.SubSetEvaluator(packer)
    optimizer = ga.GeneticOptimizer(evaluator, max_generations=GENERATIONS)
    optimizer.name = "pack item subset"
    optimizer.add_dna(ga.BitDNA.n_random(DNA_COUNT, len(packer.items)))
    print(
        f"\nGenetic algorithm search: {optimizer.name}\n"
        f"max generations={optimizer.max_generations}, DNA count={optimizer.dna_count}"
    )
    optimizer.execute(feedback, interval=3)
    print(
        f"GeneticOptimizer: {optimizer.generation} generations x {optimizer.dna_count} "
        f"DNA strands, best result:"
    )
    evaluator = cast(bp.SubSetEvaluator, optimizer.evaluator)
    best_packer = evaluator.run_packer(optimizer.best_dna)
    return best_packer


def bundle_items(items: Iterable[DXFGraphic]) -> Iterable[Bundle]:
    paths: List[Path] = list()
    for entity in items:
        p = make_path(entity)
        p.user_data = entity
        paths.append(p)
    return build_bundles(paths)


def get_packer(items: Iterable[DXFGraphic], width, height) -> bp.AbstractPacker:
    packer = bp.FlatPacker()
    packer.add_bin("B0", width, height)
    for bundle in bundle_items(items):
        box = bundle.bounding_box
        packer.add_item(bundle, box.size.x, box.size.y)
    return packer


def add_bbox(msp, box: BoundingBox, color: int):
    msp.add_lwpolyline(
        box.rect_vertices(), close=True, dxfattribs={"color": color}
    )


def make_debug_doc():
    doc = ezdxf.new()
    doc.layers.add("FRAME", color=colors.YELLOW)
    doc.layers.add("ITEMS")
    doc.layers.add("TEXT")
    return doc


class Strategy(enum.Enum):
    BIGGER_FIRST = enum.auto()
    SHUFFLE = enum.auto()
    OPTIMIZE = enum.auto()


def main(
    filename,
    bin_width: float,
    bin_height: float,
    pick=Strategy.BIGGER_FIRST,
    attempts: int = 1,
):
    try:
        doc = ezdxf.readfile(filename)
    except (IOError, ezdxf.DXFStructureError):
        print(f"IOError or invalid DXF file: '{filename}'")
        sys.exit(1)
    doc.layers.add("PACKED")
    doc.layers.add("UNFITTED")
    msp = doc.modelspace()

    packer = get_packer(msp, bin_width, bin_height)
    if pick == Strategy.SHUFFLE:
        packer = bp.shuffle_pack(packer, attempts)
    elif pick == Strategy.BIGGER_FIRST:
        packer.pack(pick=bp.PickStrategy.BIGGER_FIRST)
    elif pick == Strategy.OPTIMIZE:
        packer = run_optimizer(packer)

    envelope = packer.bins[0]
    print("packed: " + "=" * 70)
    print(f"ratio: {envelope.get_fill_ratio()}")
    for item in envelope.items:
        bundle = item.payload
        bundle.set_properties("PACKED", colors.GREEN)
        box = bundle.bounding_box
        # move entity to origin (0, 0, 0)
        bundle.transform(Matrix44.translate(-box.extmin.x, -box.extmin.y, 0))
        print(f"{str(bundle)}, size: ({box.size.x:.2f}, {box.size.y:.2f})")
        # transformation from (0, 0, 0) to final location including rotations
        m = item.get_transformation()
        bundle.transform(m)
        if DEBUG:
            add_bbox(msp, bundle.bounding_box, 5)

    print("unfitted: " + "=" * 70)
    for item in packer.unfitted_items:
        bundle = item.payload
        bundle.set_properties("UNFITTED", colors.RED)
        box = bundle.bounding_box
        print(f"{str(bundle)}, size: ({box.size.x:.2f}, {box.size.y:.2f})")
        if DEBUG:
            add_bbox(msp, box, colors.BLUE)

    # add bin frame:
    add_bbox(msp, BoundingBox([(0, 0), (bin_width, bin_height)]), colors.YELLOW)
    h = envelope.height
    w = envelope.width
    doc.set_modelspace_vport(height=h, center=(w / 2, h / 2))

    dxf_ext = ".pack.dxf"
    if pick == Strategy.OPTIMIZE:
        dxf_ext = ".opt.dxf"
    doc.saveas(filename.replace(".dxf", dxf_ext))

    if DEBUG:
        doc = make_debug_doc()
        bp.export_dxf(doc.modelspace(), packer.bins)
        doc.set_modelspace_vport(height=h, center=(w / 2, h / 2))
        doc.saveas(filename.replace(".dxf", ".debug.dxf"))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        metavar="FILE",
        nargs=1,
        help="DXF input file",
    )
    parser.add_argument(
        "width",
        metavar="WIDTH",
        type=int,
        nargs=1,
        help="width of bin",
    )
    parser.add_argument(
        "height",
        metavar="HEIGHT",
        type=int,
        nargs=1,
        help="height of bin",
    )
    parser.add_argument(
        "-o",
        "--optimize",
        action="store_true",
        default=False,
        help="use genetic algorithm optimizer",
    )
    return parser.parse_args()


if __name__ == "__main__":

    if len(sys.argv) > 1:
        args = parse_args()
        strategy = Strategy.BIGGER_FIRST
        if args.optimize:
            strategy = Strategy.OPTIMIZE
        main(args.file[0], args.width[0], args.height[0], pick=strategy)
    else:
        main(
            str("forms.dxf"),
            600,
            600,
            pick=Strategy.OPTIMIZE,
        )
