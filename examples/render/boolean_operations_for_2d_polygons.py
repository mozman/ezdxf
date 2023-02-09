# Copyright (c) 2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.render.forms import gear, translate
from ezdxf.math.clipping import (
    greiner_hormann_union,
    greiner_hormann_difference,
    greiner_hormann_intersection,
)
from ezdxf import zoom

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to execute boolean operations (union, intersection,
# difference) by the Greiner-Hormann clipping algorithm on 2D polygons.
#
# docs: https://ezdxf.mozman.at/docs/math/clipping.html
# ------------------------------------------------------------------------------

PATCH = [
    (0.3, 1.5),
    (8.924927791151, 12.144276424324),
    (15.730880789598, 2.627501561855),
    (2.887557565461, 0.615276783076),
    (-5.236692244506, -14.884612410891),
    (-13.715295679108, -8.86188181765),
    (-0.775863683945, -2.09940448737),
    (-3.015869519575, 2.14587216514),
    (-18.188942751518, 0.179187467964),
    (-9.008545512094, 15.195189150382),
    (0.3, 1.5),
]

SQUARE1 = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
SQUARE2 = [(10, 5), (20, 5), (20, 15), (10, 15), (10, 5)]


def export(polygons, name):
    doc = ezdxf.new()
    msp = doc.modelspace()
    for color, polygon in enumerate(polygons):
        msp.add_lwpolyline(polygon, dxfattribs={"color": color + 1})
    zoom.extents(msp, 1.1)
    doc.saveas(CWD / name)
    print(f"exported: {name}")


def execute_all_operations(p1, p2, prefix: str):
    export([p1, p2], prefix + "_source.dxf")
    export(greiner_hormann_union(p1, p2), prefix + "_union.dxf")
    export(greiner_hormann_intersection(p1, p2), prefix + "_intersection.dxf")
    export(greiner_hormann_difference(p1, p2), prefix + "_difference.dxf")
    export(
        greiner_hormann_difference(p2, p1),
        prefix + "_difference_reversed.dxf",
    )


def gear_and_patch():
    form = list(
        gear(
            16,
            top_width=1,
            bottom_width=3,
            height=2,
            outside_radius=10,
            close=True,
        )
    )
    # Important for proper results:
    # The polygons have to overlap and intersect each other!
    # Polygon points (vertices) on an edge of the other polygon do not count as
    # intersection!
    execute_all_operations(form, PATCH, "gp")


def this_does_not_work():
    # This example shows the boolean operations on non overlapping
    # and non-intersecting squares.
    # Polygon points (vertices) on an edge of the other polygon do not count as
    # intersection!
    execute_all_operations(SQUARE1, SQUARE2, "ts1")


def fixed_union_of_two_squares():
    # This example fixes the union problem of "this_does_not_work" by shifting
    # the second square just a little:
    execute_all_operations(
        SQUARE1, list(translate(SQUARE2, (-0.001, 0))), "ts2"
    )


if __name__ == "__main__":
    gear_and_patch()
    this_does_not_work()
    fixed_union_of_two_squares()
