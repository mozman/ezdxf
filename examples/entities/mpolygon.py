# Copyright (c) 2015-2021 Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf import zoom
from ezdxf.lldxf import const

DIR = Path("~/Desktop/Outbox").expanduser()


def create_simple_mpolygon_no_fill(dxfversion="R2000"):
    doc = ezdxf.new(dxfversion)
    msp = doc.modelspace()
    mpolygon = msp.add_mpolygon(color=2, fill_color=None)
    mpolygon.paths.add_polyline_path(
        [(0, 0), (0, 3), (3, 6), (6, 6), (6, 3), (3, 0)]
    )
    zoom.extents(msp)
    doc.saveas(DIR / f"simple_mpolygon_no_fill_{dxfversion}.dxf")


def create_simple_solid_filled_mpolygon(dxfversion="R2000"):
    doc = ezdxf.new(dxfversion)
    msp = doc.modelspace()
    mpolygon = msp.add_mpolygon(color=1, fill_color=5)
    mpolygon.paths.add_polyline_path(
        [(0, 0), (0, 3), (3, 6), (6, 6), (6, 3), (3, 0)]
    )
    zoom.extents(msp)
    doc.saveas(DIR / f"simple_solid_filled_mpolygon_{dxfversion}.dxf")


def create_mpolygon_with_bulge(dxfversion="R2000"):
    doc = ezdxf.new(dxfversion)
    msp = doc.modelspace()
    mpolygon = msp.add_mpolygon(color=1, fill_color=5)
    mpolygon.paths.add_polyline_path(
        [(0, 0), (0, 3, 0.5), (3, 6), (6, 6), (6, 3), (3, 0)]
    )
    zoom.extents(msp)
    doc.saveas(DIR / f"simple_mpolygon_with_bulge_{dxfversion}.dxf")


def create_simple_pattern_filled_mpolygon(dxfversion="R2000"):
    doc = ezdxf.new(dxfversion)
    msp = doc.modelspace()
    mpolygon = msp.add_mpolygon()
    mpolygon.set_pattern_fill("ANSI33", color=7, scale=0.01)
    mpolygon.paths.add_polyline_path(
        [(0, 0), (0, 3), (3, 6), (6, 6), (6, 3), (3, 0)]
    )
    zoom.extents(msp)
    doc.saveas(DIR / f"simple_pattern_filled_mpolygon_{dxfversion}.dxf")


def create_pattern_filled_mpolygon_with_bgcolor():
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    mpolygon = msp.add_hatch()  # by default a SOLID fill
    mpolygon.set_pattern_fill("ANSI33", color=7, scale=0.01)
    mpolygon.paths.add_polyline_path(
        [(0, 0), (0, 3), (3, 6), (6, 6), (6, 3), (3, 0)]
    )
    mpolygon.bgcolor = (100, 200, 100)
    zoom.extents(msp)
    doc.saveas(
        DIR / f"simple_pattern_filled_mpolygon_with_bgcolor_{dxfversion}.dxf"
    )


def using_hatch_style():
    def place_square_1(hatch, x, y):
        def shift(point):
            return x + point[0], y + point[1]

        # outer loop - flags = 1 (external) default value
        hatch.paths.add_polyline_path(
            map(shift, [(0, 0), (8, 0), (8, 8), (0, 8)])
        )
        # first inner loop - flags = 16 (outermost)
        hatch.paths.add_polyline_path(
            map(shift, [(2, 2), (7, 2), (7, 7), (2, 7)]),
            flags=const.BOUNDARY_PATH_OUTERMOST,
        )
        # any further inner loops - flags = 0 (default)
        hatch.paths.add_polyline_path(
            map(shift, [(4, 4), (6, 4), (6, 6), (4, 6)]),
            flags=const.BOUNDARY_PATH_DEFAULT,
        )

    def place_square_2(hatch, x, y):
        def shift(point):
            return x + point[0], y + point[1]

        # outer loop - flags = 1 (external) default value
        hatch.paths.add_polyline_path(
            map(shift, [(0, 0), (8, 0), (8, 8), (0, 8)])
        )
        # partly 1. inner loop - flags = 16 (outermost)
        hatch.paths.add_polyline_path(
            map(shift, [(3, 1), (7, 1), (7, 5), (3, 5)]),
            flags=const.BOUNDARY_PATH_OUTERMOST,
        )
        # partly 1. inner loop - flags = 16 (outermost)
        hatch.paths.add_polyline_path(
            map(shift, [(1, 3), (5, 3), (5, 7), (1, 7)]),
            flags=const.BOUNDARY_PATH_OUTERMOST,
        )

    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    # The hatch style tag, group code 75, is not supported for the MPOLYGON
    # entity by Autodesk products!
    # This example remains as it is, maybe I find a solution for this issue in
    # the future.

    # first create MPOLYGON entities
    hatch_style_0 = msp.add_mpolygon(
        color=3, fill_color=1, dxfattribs={"hatch_style": 0}
    )
    hatch_style_1 = msp.add_mpolygon(
        color=3, fill_color=1, dxfattribs={"hatch_style": 1}
    )
    hatch_style_2 = msp.add_mpolygon(
        color=3, fill_color=1, dxfattribs={"hatch_style": 2}
    )
    # then insert path elements to define the MPOLYGON boundaries
    place_square_1(hatch_style_0, 0, 0)
    place_square_1(hatch_style_1, 10, 0)
    place_square_1(hatch_style_2, 20, 0)

    # first create DXF mpolygon entities
    hatch_style_0b = msp.add_mpolygon(
        color=4, fill_color=2, dxfattribs={"hatch_style": 0}
    )
    hatch_style_1b = msp.add_mpolygon(
        color=4, fill_color=2, dxfattribs={"hatch_style": 1}
    )
    hatch_style_2b = msp.add_mpolygon(
        color=4, fill_color=2, dxfattribs={"hatch_style": 2}
    )

    # then insert path elements to define the MPOLYGON boundaries
    place_square_2(hatch_style_0b, 0, 10)
    place_square_2(hatch_style_1b, 10, 10)
    place_square_2(hatch_style_2b, 20, 10)
    zoom.extents(msp)
    doc.saveas(DIR / "mpolygon_with_hatch_styles.dxf")  # save DXF drawing


for dxfversion in ["R2000", "R2004", "R2007"]:
    create_simple_mpolygon_no_fill(dxfversion)
    create_simple_solid_filled_mpolygon(dxfversion)
    create_mpolygon_with_bulge(dxfversion)
    create_simple_pattern_filled_mpolygon(dxfversion)
    create_pattern_filled_mpolygon_with_bgcolor()
    using_hatch_style()
