# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
from __future__ import annotations
import pathlib
import ezdxf
from ezdxf import colors, xclip
from ezdxf.document import Drawing

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to use the ezdxf.xclip module to add a clipping path to
# INSERT entities (block references and XREFs).
# ------------------------------------------------------------------------------

BLOCK_NAME = "BaseBlock"


def make_block(doc: Drawing) -> str:
    blk = doc.blocks.new(BLOCK_NAME)
    blk.add_lwpolyline([(0, 0), (5, 0), (5, 5), (0, 5)], close=True)
    blk.add_line((0, 2.5), (5, 2.5), dxfattribs={"color": colors.RED})
    blk.add_line((2.5, 0), (2.5, 5), dxfattribs={"color": colors.GREEN})
    blk.add_circle((2.5, 2.5), 2.5, dxfattribs={"color": colors.BLUE})
    return BLOCK_NAME


def add_clipping_path_in_block_coordinates():
    doc = ezdxf.new()
    msp = doc.modelspace()

    name = make_block(doc)
    insert0 = msp.add_blockref(name, (10, 10))

    # The XClip class has a similar functionality as the XCLIP command in CAD applications
    clipper = xclip.XClip(insert0)

    # Define the clipping in BLOCK coordinates, this is the coordinate system with that
    # the content of the BLOCK was created.
    # The clipping path is a triangle:
    clipper.set_block_clipping_path([(0, 0), (5, 0), (2.5, 5)])
    # The procedure is executed immediately, no finalizing required.

    # Adding a rectangular clipping path defined by 2 vertices:
    insert1 = msp.add_blockref(name, (20, 10))
    clipper = xclip.XClip(insert1)
    clipper.set_block_clipping_path([(0, 1), (5, 4)])

    doc.set_modelspace_vport(height=20, center=(15, 10))
    filename = CWD / "add_clipping_path_in_block_coordinates.dxf"
    doc.saveas(filename)
    print(f"created: {filename}")


def add_clipping_path_in_wcs_coordinates():
    # same as above but the clipping paths are set in world coordinates (WCS).
    doc = ezdxf.new()
    msp = doc.modelspace()

    name = make_block(doc)
    insert0 = msp.add_blockref(name, (10, 10))

    clipper = xclip.XClip(insert0)

    # Define the clipping in WCS coordinates, this is the coordinate system in which
    # the block reference is displayed
    # The clipping path is a triangle:
    clipper.set_wcs_clipping_path([(10, 10), (15, 10), (12.5, 15)])

    # Adding a rectangular clipping path defined by 2 vertices:
    insert1 = msp.add_blockref(name, (20, 10))
    clipper = xclip.XClip(insert1)
    clipper.set_wcs_clipping_path([(20, 11), (25, 14)])

    doc.set_modelspace_vport(height=20, center=(15, 10))
    filename = CWD / "add_clipping_path_in_wcs_coordinates.dxf"
    doc.saveas(filename)
    print(f"created: {filename}")


def add_inverted_clipping_path():
    # ------------------------------------------------------------------------------
    # WARNING: The created DXF document is not compatible to AutoCAD!
    # AutoCAD will not load DXF files with inverted clipping paths created by ezdxf.
    # ------------------------------------------------------------------------------
    doc = ezdxf.new()
    msp = doc.modelspace()

    name = make_block(doc)
    insert0 = msp.add_blockref(name, (10, 10))

    # The XClip class has a similar functionality as the XCLIP command in CAD applications
    clipper = xclip.XClip(insert0)

    # Define the clipping in BLOCK coordinates, this is the coordinate system with that
    # the content of the BLOCK was created.
    # The clipping path is a triangle:
    clipper.set_block_clipping_path([(2.5, 4), (1, 1), (4, 1)])

    # invert the clipping path - the content of the triangle is invisible
    clipper.invert_clipping_path(ignore_acad_compatibility=True)

    # Adding a rectangular clipping path defined by 2 vertices:
    insert1 = msp.add_blockref(name, (20, 10))
    clipper = xclip.XClip(insert1)
    clipper.set_block_clipping_path([(1, 1), (4, 4)])
    # invert the clipping path - the content of the rectangle is invisible
    clipper.invert_clipping_path()

    doc.set_modelspace_vport(height=20, center=(15, 10))
    filename = CWD / "add_inverted_clipping_path.dxf"
    doc.saveas(filename)
    print(f"created: {filename}")


def main():
    add_clipping_path_in_block_coordinates()
    add_clipping_path_in_wcs_coordinates()
    add_inverted_clipping_path()


if __name__ == "__main__":
    main()
