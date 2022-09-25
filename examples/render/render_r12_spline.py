# Copyright (c) 2018-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.render import R12Spline
from ezdxf.math import Vec3, Matrix44, UCS, OCS

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to get B-splines in DXF R12 files which does not support
# the SPLINE entity.
# ------------------------------------------------------------------------------

next_frame = Matrix44.translate(0, 7, 0)

SEGMENTS = 40


def draw(msp, points, extrusion=None):
    dxfattribs = {"color": 1}
    if extrusion is not None:
        ocs = OCS(extrusion)
        points = ocs.points_from_wcs(points)
        dxfattribs["extrusion"] = extrusion

    for point in points:
        msp.add_circle(radius=0.1, center=point, dxfattribs=dxfattribs)


def main(dxfversion="R12"):
    doc = ezdxf.new(dxfversion)
    msp = doc.modelspace()
    spline_points = Vec3.list(
        [
            (8.55, 2.96),
            (8.55, -0.03),
            (2.75, -0.03),
            (2.76, 3.05),
            (4.29, 1.78),
            (6.79, 3.05),
        ]
    )

    # open quadratic b-spline
    draw(msp, spline_points)
    msp.add_text(
        "Open Quadratic R12Spline", dxfattribs={"height": 0.1}
    ).set_placement(spline_points[0])
    R12Spline(spline_points, degree=2, closed=False).render(
        msp, segments=SEGMENTS, dxfattribs={"color": 3}
    )
    if doc.dxfversion > "AC1009":
        msp.add_open_spline(
            control_points=spline_points, degree=2, dxfattribs={"color": 4}
        )

    # open cubic b-spline
    spline_points = list(next_frame.transform_vertices(spline_points))
    draw(msp, spline_points)
    msp.add_text(
        "Open Cubic R12Spline", dxfattribs={"height": 0.1}
    ).set_placement(spline_points[0])
    R12Spline(spline_points, degree=3, closed=False).render(
        msp, segments=SEGMENTS, dxfattribs={"color": 3}
    )
    if doc.dxfversion > "AC1009":
        msp.add_open_spline(
            control_points=spline_points, degree=3, dxfattribs={"color": 4}
        )

    # closed cubic b-spline
    spline_points = list(next_frame.transform_vertices(spline_points))
    draw(msp, spline_points)
    msp.add_text(
        "Closed Cubic R12Spline", dxfattribs={"height": 0.1}
    ).set_placement(spline_points[0])
    R12Spline(spline_points, degree=3, closed=True).render(
        msp, segments=SEGMENTS, dxfattribs={"color": 3}
    )

    # place open cubic b-spline in 3D space
    ucs = UCS(
        origin=(10, 3, 3), ux=(1, 0, 0), uz=(0, 1, 1)
    )  # 45 deg rotated around x-axis
    assert ucs.is_cartesian
    draw(msp, ucs.points_to_wcs(spline_points), extrusion=ucs.uz)
    msp.add_text(
        "Open Cubic R12Spline in 3D space",
        dxfattribs={
            "height": 0.1,
            "extrusion": ucs.uz,
        },
    ).set_placement(ucs.to_ocs(Vec3(spline_points[0])))
    R12Spline(spline_points, degree=3, closed=False).render(
        msp, segments=SEGMENTS, ucs=ucs, dxfattribs={"color": 3}
    )

    filename = CWD / f"spline_{dxfversion}.dxf"
    doc.saveas(filename)
    print(f"drawing {filename} created.")


if __name__ == "__main__":
    main()
