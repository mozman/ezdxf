#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

from pathlib import Path
import ezdxf
from ezdxf import path, zoom
from ezdxf.math import Matrix44

CWD = Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = Path(".")

# ------------------------------------------------------------------------------
# This example shows how triangulate arbitrary path objects, a doughnut in this
# special case.
#
# docs: https://ezdxf.mozman.at/docs/path.html#ezdxf.path.triangulate
# ------------------------------------------------------------------------------


def main():
    doc = ezdxf.new()
    msp = doc.modelspace()

    circle0 = path.unit_circle(segments=8)
    circle1 = circle0.transform(Matrix44.scale(3))

    colors = [1, 2, 3, 4, 5, 6, 7]
    count = len(colors)
    for index, points in enumerate(path.triangulate([circle1, circle0])):
        msp.add_solid(points, dxfattribs={"color": colors[index % count]})

    zoom.extents(msp)
    doc.saveas(CWD / "triangulated_doughnut.dxf")


if __name__ == "__main__":
    main()
