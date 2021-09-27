# Purpose: using radius DIMENSION
# Copyright (c) 2019-2021, Manfred Moitzi
# License: MIT License
import pathlib
import math
import ezdxf
from ezdxf.math import Vec3, UCS
import logging

# ========================================
# Setup logging
# ========================================
logging.basicConfig(level="WARNING")

# ========================================
# Setup your preferred output directory
# ========================================
OUTDIR = pathlib.Path("~/Desktop/Outbox").expanduser()
if not OUTDIR.exists():
    OUTDIR = pathlib.Path()

# ========================================
# Default text attributes
# ========================================
TEXT_ATTRIBS = {
    "height": 0.25,
    "style": ezdxf.options.default_dimension_text_style,
}
DIM_TEXT_STYLE = ezdxf.options.default_dimension_text_style

# =======================================================
# Discarding dimension rendering is possible
# for BricsCAD, but is incompatible to AutoCAD -> error
# =======================================================
BRICSCAD = False


def multiple_locations(delta=10, center=(0, 0)):
    cx, cy = center
    return [
        (cx + delta, cy),
        (cx + delta, cy + delta),
        (cx, cy + delta),
        (cx - delta, cy + delta),
        (cx - delta, cy),
        (cx - delta, cy - delta),
        (cx, cy - delta),
        (cx + delta, cy - delta),
    ]


def diameter_default_outside(dxfversion="R2000", delta=10):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    for x, y in multiple_locations(delta=delta):
        angle = Vec3(x, y).angle_deg
        msp.add_circle((x, y), radius=3)

        # Default DimStyle EZ_RADIUS: 1 drawing unit == 1m; scale 1: 100; length_factor=100 -> measurement in cm
        # closed filled arrow, size 0.25
        # DIMSTYLE settings:
        # dimtmove = 1: use leader, is the best setting for text outside to preserve appearance of DIMENSION entity,
        # if editing afterwards in BricsCAD (AutoCAD)

        # center: specifies the center of the circle
        # radius: specifies the radius of the circle
        # angle: specifies the the orientation (angle) of the dimension line
        dim = msp.add_diameter_dim(
            center=(x, y), radius=3, angle=angle, dimstyle="EZ_RADIUS"
        )

        # Necessary second step, to create the BLOCK entity with the DIMENSION geometry.
        # ezdxf supports DXF R2000 attributes for DXF R12 rendering, but they have to be applied by the DIMSTYLE override
        # feature, this additional attributes are not stored in the XDATA section of the DIMENSION entity, they are just
        # used to render the DIMENSION entity.
        # The return value `dim` is not a DIMENSION entity, instead a DimStyleOverride object is returned, the DIMENSION
        # entity is stored as dim.dimension, see also ezdxf.override.DimStyleOverride class.
        dim.render(discard=BRICSCAD)
    doc.set_modelspace_vport(height=3 * delta)
    doc.saveas(OUTDIR / f"dim_diameter_{dxfversion}_default_outside.dxf")


def diameter_default_inside(dxfversion="R2000", delta=10, dimtmove=0):
    def add_dim(x, y, dimtad):
        msp.add_circle((x, y), radius=3)
        dim = msp.add_diameter_dim(
            center=(x, y),
            radius=3,
            angle=angle,
            dimstyle="EZ_RADIUS_INSIDE",
            override={
                "dimtad": dimtad,
            },
        )
        dim.render(discard=BRICSCAD)

    doc = ezdxf.new(dxfversion, setup=True)
    style = doc.dimstyles.get("EZ_RADIUS_INSIDE")
    style.dxf.dimtmove = dimtmove

    # Default DimStyle EZ_RADIUS_INSIDE: 1 drawing unit == 1m; scale 1: 100; length_factor=100 -> measurement in cm
    # closed filled arrow, size 0.25
    # DIMSTYLE settings:
    # dimtmove = 0: keep dim line with text, is the best setting for text inside to preserve appearance of
    # DIMENSION entity, if editing afterwards in BricsCAD (AutoCAD)
    # dimtix = 1:   force text inside
    # dimatfit = 0: force text inside, required by BricsCAD (AutoCAD)
    # dimtad = 0: center text vertical, BricsCAD (AutoCAD) always creates vertical centered text,
    # ezdxf let you choose the vertical placement (above, below, center),
    # but editing the DIMENSION in BricsCAD will reset text to center placement.

    msp = doc.modelspace()
    for x, y in multiple_locations(delta=delta):
        angle = Vec3(x, y).angle_deg
        add_dim(x, y, dimtad=1)  # above
        add_dim(x + 3 * delta, y, dimtad=0)  # center
        add_dim(x + 6 * delta, y, dimtad=4)  # below

    doc.set_modelspace_vport(height=3 * delta)
    doc.saveas(
        OUTDIR
        / f"dim_diameter_{dxfversion}_default_inside_dimtmove_{dimtmove}.dxf"
    )


def diameter_default_outside_horizontal(dxfversion="R2000", delta=10):
    def add_dim(x, y, dimtad):
        msp.add_circle((x, y), radius=3)
        dim = msp.add_diameter_dim(
            center=(x, y),
            radius=3,
            angle=angle,
            dimstyle="EZ_RADIUS",
            override={
                "dimtoh": 1,  # force text outside horizontal
                "dimtad": dimtad,
            },
        )
        dim.render(discard=BRICSCAD)

    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    for x, y in multiple_locations(delta=delta):
        angle = Vec3(x, y).angle_deg
        add_dim(x, y, dimtad=1)  # above
        add_dim(x + 3 * delta, y, dimtad=0)  # center
        add_dim(x + 6 * delta, y, dimtad=4)  # below

    doc.set_modelspace_vport(height=3 * delta, center=(4.5 * delta, 0))
    doc.saveas(
        OUTDIR / f"dim_diameter_{dxfversion}_default_outside_horizontal.dxf"
    )


def diameter_default_inside_horizontal(
    dxfversion="R2000", delta=10, dimtmove=0
):
    doc = ezdxf.new(dxfversion, setup=True)
    style = doc.dimstyles.get("EZ_RADIUS_INSIDE")
    style.dxf.dimtmove = dimtmove

    msp = doc.modelspace()
    for x, y in multiple_locations(delta=delta):
        angle = Vec3(x, y).angle_deg
        msp.add_circle((x, y), radius=3)

        dim = msp.add_diameter_dim(
            center=(x, y),
            radius=3,
            angle=angle,
            dimstyle="EZ_RADIUS_INSIDE",
            override={
                "dimtih": 1,  # force text inside horizontal
            },
        )
        dim.render(discard=BRICSCAD)
    doc.set_modelspace_vport(height=3 * delta)
    doc.saveas(
        OUTDIR
        / f"dim_diameter_{dxfversion}_default_inside_horizontal_dimtmove_{dimtmove}.dxf"
    )


def diameter_user_defined_outside(dxfversion="R2000", delta=15):
    def add_dim(x, y, radius, dimtad):
        center = Vec3(x, y)
        msp.add_circle((x, y), radius=3)
        dim_location = center + Vec3.from_deg_angle(angle, radius)
        dim = msp.add_diameter_dim(
            center=(x, y),
            radius=3,
            location=dim_location,
            dimstyle="EZ_RADIUS",
            override={
                "dimtad": dimtad,
            },
        )
        dim.render(discard=BRICSCAD)

    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    for x, y in multiple_locations(delta=delta):
        angle = Vec3(x, y).angle_deg
        add_dim(x, y, 5, dimtad=1)  # above
        add_dim(x + 3 * delta, y, 5, dimtad=0)  # center
        add_dim(x + 6 * delta, y, 5, dimtad=4)  # below

    doc.set_modelspace_vport(height=3 * delta, center=(4.5 * delta, 0))
    doc.saveas(OUTDIR / f"dim_diameter_{dxfversion}_user_defined_outside.dxf")


def diameter_user_defined_outside_horizontal(dxfversion="R2000", delta=15):
    def add_dim(x, y, radius, dimtad):
        center = Vec3(x, y)
        msp.add_circle((x, y), radius=3)
        dim_location = center + Vec3.from_deg_angle(angle, radius)
        dim = msp.add_diameter_dim(
            center=(x, y),
            radius=3,
            location=dim_location,
            dimstyle="EZ_RADIUS",
            override={
                "dimtad": dimtad,
                "dimtoh": 1,  # force text outside horizontal
            },
        )
        dim.render(discard=BRICSCAD)

    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    for x, y in multiple_locations(delta=delta):
        angle = Vec3(x, y).angle_deg
        add_dim(x, y, 5, dimtad=1)  # above
        add_dim(x + 3 * delta, y, 5, dimtad=0)  # center
        add_dim(x + 6 * delta, y, 5, dimtad=4)  # below

    doc.set_modelspace_vport(height=3 * delta, center=(4.5 * delta, 0))
    doc.saveas(
        OUTDIR
        / f"dim_diameter_{dxfversion}_user_defined_outside_horizontal.dxf"
    )


def diameter_user_defined_inside(dxfversion="R2000", delta=10, dimtmove=0):
    def add_dim(x, y, radius, dimtad):
        center = Vec3(x, y)
        msp.add_circle((x, y), radius=3)
        dim_location = center + Vec3.from_deg_angle(angle, radius)
        dim = msp.add_diameter_dim(
            center=(x, y),
            radius=3,
            location=dim_location,
            dimstyle="EZ_RADIUS",
            override={
                "dimtad": dimtad,
            },
        )
        dim.render(discard=BRICSCAD)

    doc = ezdxf.new(dxfversion, setup=True)
    style = doc.dimstyles.get("EZ_RADIUS")
    style.dxf.dimtmove = dimtmove

    msp = doc.modelspace()
    for x, y in multiple_locations(delta=delta):
        angle = Vec3(x, y).angle_deg
        add_dim(x, y, 1, dimtad=1)  # above
        add_dim(x + 3 * delta, y, 1, dimtad=0)  # center
        add_dim(x + 6 * delta, y, 1, dimtad=4)  # below

    doc.set_modelspace_vport(height=3 * delta, center=(4.5 * delta, 0))
    doc.saveas(
        OUTDIR
        / f"dim_diameter_{dxfversion}_user_defined_inside_dimtmove_{dimtmove}.dxf"
    )


def diameter_user_defined_inside_horizontal(dxfversion="R2000", delta=10):
    def add_dim(x, y, radius, dimtad):
        center = Vec3(x, y)
        msp.add_circle((x, y), radius=3)
        dim_location = center + Vec3.from_deg_angle(angle, radius)
        dim = msp.add_diameter_dim(
            center=(x, y),
            radius=3,
            location=dim_location,
            dimstyle="EZ_RADIUS",
            override={
                "dimtad": dimtad,
                "dimtih": 1,  # force text inside horizontal
            },
        )
        dim.render(discard=BRICSCAD)

    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    for x, y in multiple_locations(delta=delta):
        angle = Vec3(x, y).angle_deg
        add_dim(x, y, 1, dimtad=1)  # above
        add_dim(x + 3 * delta, y, 1, dimtad=0)  # center
        add_dim(x + 6 * delta, y, 1, dimtad=4)  # below

    doc.set_modelspace_vport(height=3 * delta, center=(4.5 * delta, 0))
    doc.saveas(
        OUTDIR / f"dim_diameter_{dxfversion}_user_defined_inside_horizontal.dxf"
    )


def diameter_3d(dxfversion="R2000", delta=10):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()

    for x, y in multiple_locations(delta=delta):
        ucs = UCS(origin=(x, y, 0)).rotate_local_x(math.radians(45))
        angle = Vec3(x, y).angle_deg
        msp.add_circle((0, 0), radius=3).transform(ucs.matrix)
        dim = msp.add_diameter_dim(
            center=(0, 0), radius=3, angle=angle, dimstyle="EZ_RADIUS"
        )
        dim.render(discard=BRICSCAD, ucs=ucs)

    doc.set_modelspace_vport(height=3 * delta)
    doc.saveas(OUTDIR / f"dim_diameter_{dxfversion}_3d.dxf")


if __name__ == "__main__":
    diameter_default_outside()
    diameter_default_inside(dimtmove=0)  # dimline from center
    diameter_default_inside(dimtmove=1)  # dimline from text
    diameter_default_outside_horizontal()
    diameter_default_inside_horizontal(dimtmove=0)  # dimline from center
    diameter_default_inside_horizontal(dimtmove=1)  # dimline from text
    diameter_user_defined_outside()
    diameter_user_defined_outside_horizontal()
    diameter_user_defined_inside(dimtmove=0)  # dimline from text, also for 1
    diameter_user_defined_inside(dimtmove=2)  # dimline from center
    diameter_user_defined_inside_horizontal()
    diameter_3d()
