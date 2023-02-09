# Copyright (c) 2015-2022 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf import zoom
from ezdxf.lldxf import const
from ezdxf.math import Vec2

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# Multiple example for creating a HATCH entity.
#
# docs: https://ezdxf.mozman.at/docs/dxfentities/hatch.html
# tutorial: https://ezdxf.mozman.at/docs/tutorials/hatch.html
# ------------------------------------------------------------------------------


def create_solid_polyline_hatch():
    doc = ezdxf.new("R2010")  # create a new DXF drawing (AutoCAD 2010)
    msp = doc.modelspace()  # we are working in model space
    hatch = msp.add_hatch(color=2)  # by default a SOLID fill
    # if only 1 path - flags = 1 (external) by default
    hatch.paths.add_polyline_path(
        [(0, 0), (0, 3), (3, 6), (6, 6), (6, 3), (3, 0)]
    )
    zoom.extents(msp)
    doc.saveas(CWD / "hatch_solid_polyline.dxf")  # save DXF drawing


def create_pattern_fill_polyline_hatch():
    doc = ezdxf.new("R2010")  # create a new DXF drawing (AutoCAD 2010)
    msp = doc.modelspace()  # we are working in model space
    hatch = msp.add_hatch()  # by default a SOLID fill
    hatch.set_pattern_fill("ANSI33", color=7, scale=0.01)
    # if only 1 path - flags = 1 (external) by default
    hatch.paths.add_polyline_path(
        [(0, 0), (0, 3), (3, 6), (6, 6), (6, 3), (3, 0)]
    )
    zoom.extents(msp)
    doc.saveas(CWD / "hatch_pattern_fill_polyline.dxf")


def create_user_pattern_fill():
    doc = ezdxf.new("R2010")  # create a new DXF drawing (AutoCAD 2010)
    msp = doc.modelspace()  # we are working in model space
    hatch = msp.add_hatch()  # by default a SOLID fill
    offset = Vec2.from_deg_angle(45+90, length=0.7)
    hatch.set_pattern_fill(
        "MyPattern",
        color=7,
        angle=0,
        scale=1.0,
        style=0,
        pattern_type=0,
        definition=[
            [0, (0, 0), (0, 1), [1, -1]],  # horizontal dashed line
            [45, (0, 0), offset, []],  # slanted solid line
        ],
    )
    points = [(0, 0), (10, 0), (10, 10), (0, 10)]
    hatch.paths.add_polyline_path(points)
    msp.add_lwpolyline(points, close=True, dxfattribs={"color": 1})
    zoom.extents(msp)
    doc.saveas(CWD / "hatch_user_pattern_fill.dxf")


def create_pattern_fill_hatch_with_bgcolor():
    doc = ezdxf.new("R2010")  # create a new DXF drawing (AutoCAD 2010)
    msp = doc.modelspace()  # we are working in model space
    hatch = msp.add_hatch()  # by default a SOLID fill
    hatch.set_pattern_fill("ANSI33", color=7, scale=0.01)
    # if only 1 path - flags = 1 (external) by default
    hatch.paths.add_polyline_path(
        [(0, 0), (0, 3), (3, 6), (6, 6), (6, 3), (3, 0)]
    )
    hatch.bgcolor = (100, 200, 100)
    zoom.extents(msp)
    doc.saveas(CWD / "hatch_pattern_fill_with_bgcolor.dxf")


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

    doc = ezdxf.new("R2010")  # create a new DXF drawing (AutoCAD 2010)
    msp = doc.modelspace()  # we are working in model space
    # first create DXF hatch entities
    hatch_style_0 = msp.add_hatch(color=3, dxfattribs={"hatch_style": 0})
    hatch_style_1 = msp.add_hatch(color=3, dxfattribs={"hatch_style": 1})
    hatch_style_2 = msp.add_hatch(color=3, dxfattribs={"hatch_style": 2})
    # then insert path elements to define the hatch boundaries
    place_square_1(hatch_style_0, 0, 0)
    place_square_1(hatch_style_1, 10, 0)
    place_square_1(hatch_style_2, 20, 0)

    # first create DXF hatch entities
    hatch_style_0b = msp.add_hatch(color=4, dxfattribs={"hatch_style": 0})
    hatch_style_1b = msp.add_hatch(color=4, dxfattribs={"hatch_style": 1})
    hatch_style_2b = msp.add_hatch(color=4, dxfattribs={"hatch_style": 2})
    # then insert path elements to define the hatch boundaries
    place_square_2(hatch_style_0b, 0, 10)
    place_square_2(hatch_style_1b, 10, 10)
    place_square_2(hatch_style_2b, 20, 10)
    zoom.extents(msp)
    doc.saveas(CWD / "hatch_styles_examples.dxf")


def using_hatch_style_with_edge_path():
    def add_edge_path(paths, vertices, flags=1):
        path = paths.add_edge_path(flags)  # create a new edge path
        first_point = next(vertices)  # store first point for closing path
        last_point = first_point
        for next_point in vertices:
            path.add_line(last_point, next_point)  # add lines to edge path
            last_point = next_point
        path.add_line(last_point, first_point)  # close path

    def place_square_1(hatch, x, y):
        def shift(point):
            return x + point[0], y + point[1]

        # outer loop - flags=1 (external) default value
        add_edge_path(
            hatch.paths,
            map(shift, [(0, 0), (12.5, 0), (12.5, 12.5), (0, 12.5)]),
        )
        # first inner loop - flags=16 (outermost)
        add_edge_path(
            hatch.paths,
            map(shift, [(2.5, 2.5), (10, 2.5), (10, 10), (2.5, 10)]),
            flags=const.BOUNDARY_PATH_OUTERMOST,
        )
        # any inner loop - flags=0 (default)
        add_edge_path(
            hatch.paths,
            map(shift, [(5, 5), (7.5, 5), (7.5, 7.5), (5, 7.5)]),
            flags=const.BOUNDARY_PATH_DEFAULT,
        )

    def place_square_2(hatch, x, y):
        def shift(point):
            return x + point[0], y + point[1]

        add_edge_path(
            hatch.paths, map(shift, [(0, 0), (0, 8), (8, 8), (8, 0)])
        )  # 1. path
        add_edge_path(
            hatch.paths,
            map(shift, [(3, 1), (7, 1), (7, 5), (3, 5)]),
            flags=const.BOUNDARY_PATH_OUTERMOST,
        )
        add_edge_path(
            hatch.paths,
            map(shift, [(1, 3), (5, 3), (5, 7), (1, 7)]),
            flags=const.BOUNDARY_PATH_OUTERMOST,
        )

    doc = ezdxf.new("R2010")  # create a new DXF drawing (AutoCAD 2010)
    msp = doc.modelspace()  # we are working in model space
    # first create DXF hatch entities
    hatch_style_0 = msp.add_hatch(color=3, dxfattribs={"hatch_style": 0})
    hatch_style_1 = msp.add_hatch(color=3, dxfattribs={"hatch_style": 1})
    hatch_style_2 = msp.add_hatch(color=3, dxfattribs={"hatch_style": 2})
    # then insert path elements to define the hatch boundaries
    place_square_1(hatch_style_0, 0, 0)
    place_square_1(hatch_style_1, 15, 0)
    place_square_1(hatch_style_2, 30, 0)

    # first create DXF hatch entities
    hatch_style_0b = msp.add_hatch(color=4, dxfattribs={"hatch_style": 0})
    hatch_style_1b = msp.add_hatch(color=4, dxfattribs={"hatch_style": 1})
    hatch_style_2b = msp.add_hatch(color=4, dxfattribs={"hatch_style": 2})
    # then insert path elements to define the hatch boundaries
    place_square_2(hatch_style_0b, 0, 15)
    place_square_2(hatch_style_1b, 15, 15)
    place_square_2(hatch_style_2b, 30, 15)
    zoom.extents(msp)
    doc.saveas(CWD / "hatch_styles_examples_with_edge_path.dxf")


def using_hatch_with_spline_edge():
    doc = ezdxf.new("R2010")  # create a new DXF drawing (AutoCAD 2010)
    msp = doc.modelspace()  # we are working in model space
    # draw outline
    fitpoints = [(8, 0, 0), (10, 2, 0), (6, 6, 0), (8, 8, 0)]
    msp.add_line((8, 8), (0, 8))
    msp.add_line((0, 8), (0, 0))
    msp.add_line((0, 0), (8, 0))
    # use spline with control points created by ezdxf
    # Don't know how AutoCAD calculates control points from fit points
    msp.add_spline_control_frame(fit_points=fitpoints)

    # next create DXF hatch entities
    hatch = msp.add_hatch(color=3)
    # if only 1 path - flags = 1 (external) by default
    path = hatch.paths.add_edge_path()  # create a new edge path
    path.add_line((8, 8), (0, 8))
    path.add_line((0, 8), (0, 0))
    path.add_line((0, 0), (8, 0))
    path.add_spline_control_frame(fit_points=fitpoints)
    zoom.extents(msp)
    doc.saveas(CWD / "hatch_with_spline_edge.dxf")  # save DXF drawing


if __name__ == "__main__":
    #create_solid_polyline_hatch()
    #create_pattern_fill_polyline_hatch()
    #create_pattern_fill_hatch_with_bgcolor()
    create_user_pattern_fill()
    #using_hatch_style()
    #using_hatch_style_with_edge_path()
    #using_hatch_with_spline_edge()
