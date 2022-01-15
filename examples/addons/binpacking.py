#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Iterable, List
import ezdxf
from ezdxf.entities import DXFGraphic
from ezdxf.math import Matrix44, BoundingBox, Vec3
from ezdxf.path import Path, make_path, nesting
from ezdxf.addons import binpacking

UNLIMITED = 1_000_000
WEIGHT = 0
DEBUG_BOXES = True


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


def bundle_items(items: Iterable[DXFGraphic]) -> Iterable[Bundle]:
    paths: List[Path] = list()
    for entity in items:
        p = make_path(entity)
        p.user_data = entity
        paths.append(p)
    return build_bundles(paths)


def pack(items: Iterable[DXFGraphic], width, height):
    packer = binpacking.FlatPacker()
    packer.add_envelope("B0", width, height)
    for bundle in bundle_items(items):
        box = bundle.bounding_box
        packer.add_item(bundle, box.size.x, box.size.y)
    packer.pack(pick_strategy=binpacking.PickStrategy.BIGGER_FIRST)
    return packer


def add_bbox(msp, box: BoundingBox, color: int):
    msp.add_lwpolyline(
        box.rect_vertices(), close=True, dxfattribs={"color": color}
    )


def main(filename, bin_width, bin_height):
    doc = ezdxf.readfile(filename)
    doc.layers.add("PACKED")
    doc.layers.add("UNFITTED")
    msp = doc.modelspace()
    packer = pack(msp, bin_width, bin_height)
    envelope = packer.bins[0]
    print("packed: " + "=" * 70)
    color = 3
    for item in envelope.items:
        if color == 3:
            color = 6
        else:
            color = 3
        bundle = item.payload
        bundle.set_properties("PACKED", color)
        box = bundle.bounding_box
        # move entity to origin (0, 0, 0)
        bundle.transform(Matrix44.translate(-box.extmin.x, -box.extmin.y, 0))
        print(f"{str(bundle)}, size: ({box.size.x:.2f}, {box.size.y:.2f})")
        # transformation from (0, 0, 0) to final location including rotations
        m = item.get_transformation()
        bundle.transform(m)
        if DEBUG_BOXES:
            add_bbox(msp, bundle.bounding_box, 5)

    print("unfitted: " + "=" * 70)
    for item in envelope.unfitted_items:
        bundle = item.payload
        bundle.set_properties("UNFITTED", 2)
        box = bundle.bounding_box
        print(f"{str(bundle)}, size: ({box.size.x:.2f}, {box.size.y:.2f})")
        if DEBUG_BOXES:
            add_bbox(msp, box, 5)

    # add bin frame:
    add_bbox(msp, BoundingBox([(0, 0), (bin_width, bin_height)]), 1)
    doc.saveas(filename.replace(".dxf", ".pack.dxf"))
    doc2 = binpacking.export_dxf(packer, Vec3(0, 0, 1))
    doc2.saveas(filename.replace(".dxf", ".debug.dxf"))


if __name__ == "__main__":
    main(r"C:\Users\manfred\Desktop\Now\ezdxf\binpacking\items.dxf", 60, 60)
    main(r"C:\Users\manfred\Desktop\Now\ezdxf\binpacking\case.dxf", 500, 600)
