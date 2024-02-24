# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from pathlib import Path
import dataclasses
import ezdxf

from ezdxf.math import Vec3, OCS, normal_vector_3p, ConstructionCircle

CWD = Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = Path(".")

# ------------------------------------------------------------------------------
# This example adds a circle from 3 arbitrary points in 3D to the modelspace.
#
# Example how to use the OCS to place 2D entities in 3D space.
#
# docs: https://ezdxf.mozman.at/docs/dxfentities/circle.html
# ------------------------------------------------------------------------------


@dataclasses.dataclass
class CircleOCS:
    center: Vec3
    radius: float
    extrusion: Vec3


def circle3p(a: Vec3, b: Vec3, c: Vec3) -> CircleOCS | None:
    try:
        extrusion = normal_vector_3p(a, b, c)
    except ZeroDivisionError:
        # no solution
        return None
    ocs = OCS(extrusion)
    # transform vertices from WCS to OCS
    o0, o1, o2 = ocs.points_from_wcs([a, b, c])
    elevation = o0.z
    # All three points have the same elevation! 
    # That's the basic concept of the OCS, all points in the xy-plane of the OCS have 
    # the same z-distance from the origin. The xy-plane of the OCS is the construction 
    # plane for 2D entities.
    circle2d = ConstructionCircle.from_3p(o0, o1, o2)

    # The entity coordinates (center for CIRCLE) are stored as OCS coordinates and the 
    # extrusion vector defines the OCS.
    center = Vec3(circle2d.center.x, circle2d.center.y, elevation)
    return CircleOCS(center, circle2d.radius, extrusion)


def main(points: list[Vec3]):
    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_polyline3d(points, close=True, dxfattribs={"color": 2})

    circle_ocs = circle3p(*points)
    if circle_ocs is not None:
        msp.add_circle(
            circle_ocs.center,
            radius=circle_ocs.radius,
            dxfattribs={"extrusion": circle_ocs.extrusion, "color": 1},
        )
        doc.saveas(CWD / "circle3p.dxf")
    else:
        print("No solution.")


if __name__ == "__main__":
    main(Vec3.list([(0, 0, 0), (1, 0, 0), (0, 0, 1)]))
