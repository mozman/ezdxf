#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from pathlib import Path
import time

import ezdxf
from ezdxf.math import Vec2, Matrix44
from ezdxf.render import forms, hatching
from ezdxf import path

CWD = Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = Path(".")


def polygon_hatching(filename: str):
    doc = ezdxf.new()
    setup(doc)
    msp = doc.modelspace()
    polygon = Vec2.list(
        forms.gear(16, top_width=1, bottom_width=3, height=2, outside_radius=10)
    )
    hole = list(forms.circle(16, radius=4))
    hole1 = Vec2.list(forms.translate(hole, (-2, -2)))
    hole2 = Vec2.list(forms.translate(hole, (2, 2)))
    baseline = hatching.HatchBaseLine(Vec2(), direction=Vec2(1, 1), offset=Vec2(-1, 1))
    render_hatch(msp, baseline, polygon, [hole1, hole2])
    doc.saveas(CWD / filename)


SIZE = 0.1


def setup(doc):
    doc.layers.add("POLYGON", color=ezdxf.colors.BLUE)
    doc.layers.add("MARKERS", color=ezdxf.colors.GREEN)
    doc.layers.add("POINTS", color=ezdxf.colors.RED)
    doc.layers.add("HATCH", color=ezdxf.colors.YELLOW)
    marker = doc.blocks.new("MARKER")
    marker.add_line((-SIZE, -SIZE), (SIZE, SIZE))
    marker.add_line((-SIZE, SIZE), (SIZE, -SIZE))


def render_hatch(msp, baseline, polygon, holes=None, offset=Vec2()):
    polygons = [Vec2.list(forms.translate(polygon, offset))]
    if holes:
        for hole in holes:
            polygons.append(Vec2.list(forms.translate(hole, offset)))
    for polygon in polygons:
        msp.add_lwpolyline(
            polygon,
            close=True,
            dxfattribs={"layer": "POLYGON"},
        )
        for p in polygon:
            msp.add_circle(
                p,
                radius=SIZE,
                dxfattribs={"layer": "POINTS"},
            )
    for line in hatching.hatch_polygons(baseline, polygons):
        msp.add_line(
            line.start,
            line.end,
            dxfattribs={"layer": "HATCH"},
        )
        msp.add_blockref("MARKER", line.start, dxfattribs={"layer": "MARKERS"})
        msp.add_blockref("MARKER", line.end, dxfattribs={"layer": "MARKERS"})


POLYGONS = [
    list(forms.turtle("10 l 10 l 10")),
    list(forms.turtle("5 r 2 l 5 l 12 l 5 r 2 l 5")),
    list(forms.turtle("5 l 2 r 5 l 10 l 5 l 2 r 5")),
    list(forms.turtle("2 l 2 r 2 r 2 l 6 " "l 10 l 2 l 2 r 2 r 2 l 6")),
    list(forms.turtle("2 l 2 r 2 l 2 r 2 r 4 l 4 l 10 l 2 l 2 r 2 l 2 r 2 r 4 l 4")),
    list(forms.turtle("2 r 2 l 2 r 2 l 2 l 4 r 4 l 10 l 2 r 2 l 2 r 2 l 2 l 4 r 4")),
    list(
        forms.turtle(
            "2 l 2 r 2 r 2 l 2 l 4 r 2 r 4 l 2 l 10 l 2 r 2 l 2 l 2 r 2 r 4 l 2 l 4 r 2"
        )
    ),
    list(forms.turtle("3 @2,2 @2,-2 3 l 10 l @-2,-2 @-2,2 2 @-2,-2 @-2,2")),
    list(
        forms.turtle(
            "3 @1,1 @1,1 @1,-1 @1,-1 3 l 10 l @-1,-1 @-1,-1 @-1,1 @-1,1 2 "
            "@-1,-1 @-1,-1 @-1,1 @-1,1"
        )
    ),
]


def collinear_horizontal_hatching(filename: str):
    doc = ezdxf.new()
    msp = doc.modelspace()
    setup(doc)
    for index, polygon in enumerate(POLYGONS):
        baseline = hatching.HatchBaseLine(
            Vec2(), direction=Vec2(1, 0), offset=Vec2(0, 1)
        )
        render_hatch(msp, baseline, polygon, offset=Vec2(12 * index, 0))
    doc.saveas(CWD / filename)


def collinear_vertical_hatching(filename: str):
    doc = ezdxf.new()
    msp = doc.modelspace()
    setup(doc)
    for index, polygon in enumerate(POLYGONS):
        baseline = hatching.HatchBaseLine(
            Vec2(), direction=Vec2(0, 1), offset=Vec2(1, 0)
        )
        render_hatch(msp, baseline, polygon, offset=Vec2(12 * index, 0))
    doc.saveas(CWD / filename)


def explode_hatch_pattern(filename: str):
    example = Path(__file__).parent.parent / "examples_dxf" / filename
    doc = ezdxf.readfile(example)
    msp = doc.modelspace()
    attribs = {"layer": "EXPLODE", "color": ezdxf.colors.RED}
    t0 = time.perf_counter()
    for hatch in msp.query("HATCH"):
        for start, end in hatching.hatch_entity(hatch):  # type: ignore
            msp.add_line(start, end, attribs)
    t1 = time.perf_counter()
    print(f"Exploding hatch pattern took: {t1-t0:.3}s")
    doc.saveas(CWD / filename.replace(".dxf", ".explode.dxf"))


def hatch_circular_path(filename: str, size=10, angle=0):
    doc = ezdxf.new()
    setup(doc)
    msp = doc.modelspace()
    m = Matrix44.scale(size)
    circle = path.unit_circle(segments=8, transform=m)
    direction = Vec2.from_deg_angle(angle)
    offset = direction.orthogonal() * 0.1
    baseline = hatching.HatchBaseLine(Vec2(0, 0), direction=direction, offset=offset)
    msp.add_lwpolyline(
        circle.flattening(0.1), close=True, dxfattribs={"layer": "POLYGON"}
    )
    for line in hatching.hatch_paths(baseline, [circle]):
        msp.add_line(
            line.start,
            line.end,
            dxfattribs={"layer": "HATCH"},
        )
    doc.saveas(CWD / filename)


def hole_examples(filename: str, size=10, dx=13, angle=0):
    doc = ezdxf.new()
    setup(doc)
    msp = doc.modelspace()
    # overlapping holes
    holes = [
        list(forms.translate(forms.square(size - 2), (1, 1))),
        list(forms.translate(forms.square(3), (2, 2))),
        list(forms.translate(forms.square(3), (4, 3))),
    ]
    direction = Vec2.from_deg_angle(angle)
    offset = direction.orthogonal() * 0.1
    baseline = hatching.HatchBaseLine(Vec2(0, 0), direction=direction, offset=offset)
    render_hatch(msp, baseline, forms.square(size), holes)
    # adjacent holes
    holes = [
        list(forms.translate(forms.square(size - 2), (1, 1))),
        list(forms.translate(forms.square(2), (2, 2))),
        list(forms.translate(forms.square(2), (6, 2))),
    ]
    render_hatch(msp, baseline, forms.square(size), holes, Vec2(dx, 0))
    # nested holes
    holes = [
        list(forms.translate(forms.square(size - 2), (1, 1))),
        list(forms.translate(forms.square(size - 4), (2, 2))),
        list(forms.translate(forms.square(size - 6), (3, 3))),
    ]
    render_hatch(msp, baseline, forms.square(size), holes, Vec2(dx * 2, 0))
    # holes extending beyond exterior polygon
    holes = [
        list(forms.translate(forms.square(4), (-1.5, -2))),
        list(forms.translate(forms.square(6), (2, 6))),
        list(forms.translate(forms.square(2), (5, 2))),
    ]
    render_hatch(msp, baseline, forms.square(size), holes, Vec2(dx * 3, 0))

    # holes extending beyond exterior polygon
    holes = [
        list(forms.translate(forms.square(3), (-1.5, -1.5))),
        list(forms.translate(forms.square(3), (5, 5))),
        list(forms.translate(forms.square(3), (8.5, 8.5))),
    ]
    render_hatch(msp, baseline, forms.square(size), holes, Vec2(dx * 4, 0))

    doc.saveas(CWD / filename)


def debug_hatch():
    # earth1 pattern
    doc = ezdxf.new()
    msp = doc.modelspace()
    e = msp.add_hatch(
        color=7,
        dxfattribs={
            "layer": "HATCH",
            "elevation": (0.0, 0.0, 0.0),
            "extrusion": (0.0, 0.0, 1.0),
            "pattern_name": "CROSS",
            "solid_fill": 0,
            "associative": 0,
            "hatch_style": 1,
            "pattern_type": 1,
            "pattern_angle": 0.0,
            "pattern_scale": 0.25,
            "pattern_double": 0,
        },
    )
    e.set_pattern_definition(
        [
            [0.0, (0.0, 0.0), (1.5875, 1.5875), [1.5875, -1.5875]],
            [0.0, (0.0, 0.5953125), (1.5875, 1.5875), [1.5875, -1.5875]],
            [0.0, (0.0, 1.190625), (1.5875, 1.5875), [1.5875, -1.5875]],
            [
                90.0,
                (0.1984375, 1.3890625),
                (-1.5875, 1.5875),
                [1.5875, -1.5875],
            ],
            [90.0, (0.79375, 1.3890625), (-1.5875, 1.5875), [1.5875, -1.5875]],
            [
                90.0,
                (1.3890625, 1.3890625),
                (-1.5875, 1.5875),
                [1.5875, -1.5875],
            ],
        ]
    )
    e.dxf.solid_fill = 0
    # 1. polyline path
    e.paths.add_polyline_path(
        [
            (0.0, 223.0, 0.0),
            (10.0, 223.0, 0.0),
            (10.0, 233.0, 0.0),
            (0.0, 233.0, 0.0),
        ],
        is_closed=1,
        flags=3,
    )
    for start, end in hatching.hatch_entity(e, 1, jiggle_origin=True):  # type: ignore
        msp.add_line(start, end)


if __name__ == "__main__":
    # debug_hatch()
    polygon_hatching("polygon_hatching.dxf")
    collinear_horizontal_hatching("collinear_horizontal_hatching.dxf")
    collinear_vertical_hatching("collinear_vertical_hatching.dxf")
    explode_hatch_pattern("hatch_pattern_iso.dxf")
    hatch_circular_path("circle_00_deg.dxf", 10, 0)
    hatch_circular_path("circle_90_deg.dxf", 10, 90)
    hatch_circular_path("circle_45_deg.dxf", 10, 45)
    hole_examples("hole_examples_00_deg.dxf", angle=0)
    hole_examples("hole_examples_90_deg.dxf", angle=90)
    hole_examples("hole_examples_45_deg.dxf", angle=45)
