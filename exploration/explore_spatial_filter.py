# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from pathlib import Path
import math
import ezdxf
from ezdxf import colors, xclip
from ezdxf.entities import Insert
from ezdxf.math import Vec2, Matrix44

OUTBOX = Path("~/Desktop/Outbox").expanduser()
if not OUTBOX.exists():
    OUTBOX = Path(".")

DEFAULT_FILES = [
    #"BlockClipped.dxf",
    #"BlockClippedBasicTransform.dxf",
    #"TransformedBlockClipped.dxf",
    #"BlockClipped_OriginOffset.dxf",
    "InvertedClippingBricsCAD.dxf",
]


def make_base_block():
    doc = ezdxf.new()
    # The HEADER variable `$XCLIPFRAME` ultimately determines whether the 
    # clipping path is displayed or plotted:
    # 0= not displayed, not plotted
    # 1= displayed, not plotted
    # 2= displayed, plotted
    doc.header["$XCLIPFRAME"] = 2
    blk = doc.blocks.new("BaseBlock", base_point=(5, 5))
    blk.add_lwpolyline([(5, 5), (10, 5), (10, 10), (5, 10)], close=True)
    blk.add_line((5, 7.5), (10, 7.5), dxfattribs={"color": colors.RED})
    blk.add_line((7.5, 5), (7.5, 10), dxfattribs={"color": colors.GREEN})
    blk.add_circle((7.5, 7.5), 2.5, dxfattribs={"color": colors.BLUE})
    msp = doc.modelspace()
    msp.add_blockref("BaseBlock", (5, 5))
    doc.saveas(OUTBOX / "BaseBlock_origin_offset.dxf")


def copy_clipped_block_defs():
    def copy_insert(
        entity: Insert, x: float, y: float, angle: float = 0.0, scale: float = 1.0
    ) -> Insert:
        new_insert = entity.copy()
        m = (
            Matrix44.scale(scale, scale, scale)
            @ Matrix44.z_rotate(math.radians(angle))
            @ Matrix44.translate(x, y, 0)
        )
        new_insert.transform(m)
        return new_insert

    script_path = Path(__file__).parent
    doc = ezdxf.readfile(script_path / "BlockClipped.dxf")
    msp = doc.modelspace()
    insert = msp[0]
    assert isinstance(insert, Insert)

    msp.add_entity(copy_insert(insert, 10, 0))
    msp.add_entity(copy_insert(insert, 10, 10, 45))
    msp.add_entity(copy_insert(insert, 0, 10, 0, 2))
    doc.saveas(OUTBOX / "transformed_clipped_blocks.dxf")



def get_boundary_vertices(insert: Insert) -> tuple[Vec2, ...]:
    vertices: tuple[Vec2, ...] = tuple()
    spatial_filter = xclip.get_spatial_filter(insert)
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
    spatial_filter = xclip.get_spatial_filter(insert)
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
    # copy_clipped_block_defs()
    main(DEFAULT_FILES)
