# Copyright (C) 2022, Manfred Moitzi
# License: MIT License

import pathlib
import ezdxf
from ezdxf.entities import Hatch, Pattern
from ezdxf.math import Vec2

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

ORIGIN = (0.5, 0.5)


def reset_pattern_origin(hatch: Hatch, origin: Vec2):
    if isinstance(hatch.pattern, Pattern):
        for pattern_line in hatch.pattern.lines:
            pattern_line.base_point = origin


def shift_pattern_origin(hatch: Hatch, offset: Vec2):
    if isinstance(hatch.pattern, Pattern):
        for pattern_line in hatch.pattern.lines:
            pattern_line.base_point += offset


def reset_pattern_origin_of_first_pattern_line(hatch: Hatch, origin: Vec2):
    if isinstance(hatch.pattern, Pattern) and len(hatch.pattern.lines):
        first_pattern_line = hatch.pattern.lines[0]
        offset = origin - first_pattern_line.base_point
        shift_pattern_origin(hatch, offset)


def main():
    doc = ezdxf.new()
    msp = doc.modelspace()

    points = [(0, 0), (10, 0), (10, 10), (0, 10)]
    msp.add_lwpolyline(points, close=True)
    hatch = msp.add_hatch()
    hatch.paths.add_polyline_path(points)
    hatch.set_pattern_fill(
        "MyPattern",
        color=7,
        angle=0,
        scale=1.0,
        style=0,  # normal hatching style
        pattern_type=0,  # user-defined
        definition=[
            [0, ORIGIN, (0, 1), []],
            [90, ORIGIN, (1, 0), []],
        ],
    )

    # setting the seed points has no effect on the pattern origin:
    # hatch.set_seed_points([(0.75, 0.75), (0.75, 0.75)])

    # resetting the origin works:
    # shift_pattern_origin(hatch, Vec2(0.5, 0.5))
    reset_pattern_origin_of_first_pattern_line(hatch, Vec2(0, 0))

    doc.set_modelspace_vport(12, center=(5, 5))
    doc.saveas(CWD / "hatch_pattern_modify_origin.dxf")


if __name__ == "__main__":
    main()
