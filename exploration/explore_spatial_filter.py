# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
from __future__ import annotations
import sys
import argparse
from pathlib import Path

import ezdxf
from ezdxf import colors
from ezdxf.entities import Insert, DXFEntity, SpatialFilter, Dictionary
from ezdxf.math import Vec2

OUTBOX = Path("~/Desktop/Outbox").expanduser()
if not OUTBOX.exists():
    OUTBOX = Path(".")

DEFAULT_FILES = [
    #"BlockClipped.dxf",
    #"BlockClippedBasicTransform.dxf",
    #"TransformedBlockClipped.dxf",
    "BlockClipped_OriginOffset.dxf",
]
ACAD_FILTER = "ACAD_FILTER"
SPATIAL = "SPATIAL"


def make_base_block():
    doc = ezdxf.new()
    blk = doc.blocks.new("BaseBlock", base_point=(5, 5))
    blk.add_lwpolyline([(5, 5), (10, 5), (10, 10), (5, 10)], close=True)
    blk.add_line((5, 7.5), (10, 7.5), dxfattribs={"color": colors.RED})
    blk.add_line((7.5, 5), (7.5, 10), dxfattribs={"color": colors.GREEN})
    blk.add_circle((7.5, 7.5), 2.5, dxfattribs={"color": colors.BLUE})
    msp = doc.modelspace()
    msp.add_blockref("BaseBlock", (5, 5))
    doc.saveas(OUTBOX / "BaseBlock_origin_offset.dxf")


def get_spatial_filter(entity: DXFEntity) -> SpatialFilter | None:
    try:
        xdict = entity.get_extension_dict()
    except AttributeError:
        return None
    acad_filter = xdict.get(ACAD_FILTER)
    if not isinstance(acad_filter, Dictionary):
        return None
    acad_spatial_filter = acad_filter.get(SPATIAL)
    if isinstance(acad_spatial_filter, SpatialFilter):
        return acad_spatial_filter
    return None


def get_boundary_vertices(insert: Insert) -> tuple[Vec2, ...]:
    vertices: tuple[Vec2, ...] = tuple()
    spatial_filter = get_spatial_filter(insert)
    if spatial_filter is None:
        return vertices
    return spatial_filter.boundary_vertices


def print_transform_params(insert: Insert) -> None:
    print(str(insert))
    print(f"  insert location: {insert.dxf.insert}")
    print(f"  rotation: {insert.dxf.rotation}")
    print(f"  scale-x: {insert.dxf.xscale}")
    print(f"  scale-y: {insert.dxf.yscale}")
    print(f"  scale-z: {insert.dxf.zscale}")
    spatial_filter = get_spatial_filter(insert)
    if spatial_filter:
        print(f"  {str(spatial_filter)}")


def show_clipping_paths(file_path: Path) -> None:
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()
    for blockref in msp.query("INSERT"):
        assert isinstance(blockref, Insert)
        print("-" * 79)
        boundary_vertices = get_boundary_vertices(blockref)
        if boundary_vertices:
            print_transform_params(blockref)
            print(f"  boundary-vertices: {str(boundary_vertices)}")
            msp.add_lwpolyline(
                boundary_vertices, close=True, dxfattribs={"layer": blockref.dxf.layer}
            )
    out_path = OUTBOX / ("Annotated-" + file_path.name)
    doc.saveas(out_path)
    print(f"file '{out_path}' created")


def main(filenames: list[str]) -> None:
    script_path = Path(__file__).parent
    for filename in filenames:
        path = Path(filename)
        for file_path in [path, script_path / path, OUTBOX / path]:
            if file_path.exists():
                show_clipping_paths(file_path)


if __name__ == "__main__":
    # make_base_block()
    main(DEFAULT_FILES)
