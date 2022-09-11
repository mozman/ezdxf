# Copyright (c) 2020-2022 Manfred Moitzi
# License: MIT License
import pathlib
import math
import ezdxf
from ezdxf import zoom
from ezdxf.math import UCS, Vec3

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to transform entities by the general transformation
# interface and the UCS class.
#
# docs:
# https://ezdxf.mozman.at/docs/dxfentities/dxfgfx.html#ezdxf.entities.DXFGraphic.transform
# https://ezdxf.mozman.at/docs/math/core.html#ucs-class
# ------------------------------------------------------------------------------

NARROW = "OpenSansCondensed-Light"
X_COUNT = 7
Y_COUNT = 7
DX = 2
DY = 2


def add_circle(msp, ucs):
    msp.add_circle(
        center=(0, 0),
        radius=0.5,
        dxfattribs={
            "color": 6,
        },
    ).transform(ucs.matrix)


def add_ocs_circle(msp, ucs):
    msp.add_circle(
        center=(0, 0, 0.5),
        radius=0.25,
        dxfattribs={
            "color": 6,
            "extrusion": (1, 0, 0),
        },
    ).transform(ucs.matrix)


def add_ellipse(msp, ucs):
    msp.add_ellipse(
        center=(0, 0),
        major_axis=(0.5, 0, 0),
        ratio=0.5,
        start_param=0,
        end_param=math.pi,
        dxfattribs={
            "color": 1,
        },
    ).transform(ucs.matrix)


def add_ocs_arc(msp, ucs):
    msp.add_arc(
        center=(0, 0, 0.5),
        radius=0.25,
        start_angle=0,
        end_angle=90,
        dxfattribs={
            "color": 4,
            "extrusion": (-1, 0, 0),
        },
    ).transform(ucs.matrix)


def add_solid(msp, ucs):
    msp.add_solid(
        [(-0.25, -0.15), (0.25, -0.15), (0, -0.5)], dxfattribs={"color": 2}
    ).transform(ucs.matrix)


def add_trace(msp, ucs):
    msp.add_trace(
        [(-0.25, 0.15), (0.25, 0.15), (0, 0.5)], dxfattribs={"color": 7}
    ).transform(ucs.matrix)


def add_3dface(msp, ucs):
    msp.add_3dface(
        [(0, 0, 0), (0.5, 0.5, 0), (0.5, 0.5, 0.5), (0, 0, 0.5)],
        dxfattribs={"color": 8},
    ).transform(ucs.matrix)


def add_lwpolyline(msp, ucs):
    msp.add_lwpolyline(
        [(0, 0, 0), (0.3, 0, 1), (0.3, 0.3, 0), (0, 0.3, 0)],
        format="xyb",
        dxfattribs={"color": 6},
    ).transform(ucs.matrix)


def add_text(msp, ucs):
    msp.add_text(
        "TEXT",
        dxfattribs={
            "color": 4,
            "style": NARROW,
            "height": 0.2,
        },
    ).set_align("MIDDLE_CENTER").transform(ucs.matrix)


def add_mtext(msp, ucs):
    # It is always better to use text_direction instead of a rotation angle,
    # which works only for extrusion == (0, 0, 1)
    msp.add_mtext(
        "MTEXT",
        dxfattribs={
            "color": 5,
            "style": NARROW,
            "char_height": 0.2,
            "insert": (0, 0),
            "rotation": 90,
            "attachment_point": 4,
        },
    ).transform(ucs.matrix)


def scene1(filename):
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()

    ucs = UCS()
    angle = math.pi / 12  # 15 degree

    for ix in range(X_COUNT):
        for iy in range(Y_COUNT):
            ucs.moveto((ix * DX, iy * DY, 0))
            ucs.render_axis(msp, length=1)
            add_circle(msp, ucs)
            # add_ocs_circle(msp, ucs)
            # add_ocs_arc(msp, ucs)
            # add_text(msp, ucs)
            add_mtext(msp, ucs)
            add_ellipse(msp, ucs)
            # add_solid(msp, ucs)
            add_trace(msp, ucs)
            # add_3dface(msp, ucs)
            # add_lwpolyline(msp, ucs)
            ucs = ucs.rotate_local_z(angle)
        ucs = UCS().rotate_local_x(ix * angle)

    zoom.extents(msp)
    doc.saveas(filename)


def add_excentric_text(msp, ucs, location, text):
    text = msp.add_mtext(
        text,
        dxfattribs={
            "color": 5,
            "style": NARROW,
            "char_height": 0.2,
            "insert": location,
            "attachment_point": 5,
        },
    )
    text.transform(ucs.matrix)
    msp.add_line(
        start=(0, 0, 0), end=(location.x, 0, 0), dxfattribs={"color": 1}
    ).transform(ucs.matrix)
    msp.add_line(
        start=(location.x, 0, 0),
        end=(location.x, location.y, 0),
        dxfattribs={"color": 3},
    ).transform(ucs.matrix)
    msp.add_line(
        start=(location.x, location.y, 0),
        end=(location.x, location.y, location.z),
        dxfattribs={"color": 5},
    ).transform(ucs.matrix)


def scene2(filename):
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()
    delta = 6
    for z in range(-2, 3):
        for y in range(-2, 3):
            for x in range(-2, 3):
                cx = x * delta
                cy = y * delta
                cz = z * delta
                ucs = (
                    UCS(origin=(cx, cy, cz))
                    .rotate_local_z(math.radians(45))
                    .rotate_local_x(math.radians(30))
                )
                add_excentric_text(
                    msp,
                    ucs,
                    location=Vec3(1, 2, 3),
                    text=f"Hallo\n(x={cx}, y={cy}, z={cz})",
                )

    zoom.extents(msp)
    doc.saveas(filename)


if __name__ == "__main__":
    scene1(CWD / "transform_scene_1.dxf")
    scene2(CWD / "transform_scene_2.dxf")
