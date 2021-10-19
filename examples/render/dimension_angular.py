# Purpose: using angular DIMENSION
# Copyright (c) 2021, Manfred Moitzi
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
BRICSCAD = True


def multiple_locations(delta=10):
    base0 = Vec3(5.8833, -6.3408)
    l1_p1 = Vec3(2.0101, -7.5156) - base0
    l1_p2 = Vec3(2.7865, -10.4133) - base0
    l2_p1 = Vec3(6.7054, -7.5156) - base0
    l2_p2 = Vec3(5.9289, -10.4133) - base0
    return [
        (Vec3(), (l1_p1, l1_p2), (l2_p1, l2_p2)),
    ]


def angular_default_above(dxfversion="R2000", delta=10):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    for base, line1, line2 in multiple_locations(delta):
        msp.add_line(line1[0], line1[1])
        msp.add_line(line2[0], line2[1])

        # Default DimStyle EZ_ANGULAR:
        # - angle units = degree
        # - scale 1: 100
        # - closed filled arrow, size = 0.25
        # - text location above dimension line
        #
        # base:
        #   location of the dimension line
        # line1:
        #   first line defining the angle
        # line2:
        #   second line defining the angle
        dim = msp.add_angular_dim(
            base=base, line1=line1, line2=line2, dimstyle="EZ_ANGULAR"
        )
        # Necessary second step, to create the BLOCK entity with the DIMENSION
        # geometry. Ezdxf supports DXF R2000 attributes for DXF R12 rendering,
        # but they have to be applied by the DIMSTYLE override feature, this
        # additional attributes are not stored in the XDATA section of the
        # DIMENSION entity, they are just used to render the DIMENSION entity.
        # The return value `dim` is not a DIMENSION entity, instead a
        # DimStyleOverride object is returned, the DIMENSION entity is stored
        # as dim.dimension, see also ezdxf.override.DimStyleOverride class.
        dim.render(discard=BRICSCAD)
    doc.set_modelspace_vport(height=3 * delta)
    doc.saveas(OUTDIR / f"dim_angular_{dxfversion}_default_above.dxf")


def angular_default_center(dxfversion="R2000", delta=10):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    for base, line1, line2 in multiple_locations(delta):
        msp.add_line(line1[0], line1[1])
        msp.add_line(line2[0], line2[1])
        dim = msp.add_angular_dim(
            base=base,
            line1=line1,
            line2=line2,
            dimstyle="EZ_ANGULAR",
            override={"dimtad": 0},
        )
        dim.render(discard=BRICSCAD)
    doc.set_modelspace_vport(height=3 * delta)
    doc.saveas(OUTDIR / f"dim_angular_{dxfversion}_default_center.dxf")

def angular_user_defined_keep_with_line(dxfversion="R2000", delta=15):
    def add_dim(x, y, radius, dimtad):
        center = Vec3(x, y)
        msp.add_circle((x, y), radius=3)
        dim_location = center + Vec3.from_deg_angle(angle, radius)
        dim = msp.add_angular_dim(
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
    doc.saveas(OUTDIR / f"dim_angular_{dxfversion}_user_defined_outside.dxf")


def angular_3d(dxfversion="R2000", delta=10):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()

    for base, line1, line2 in multiple_locations(delta=delta):
        ucs = UCS(origin=(base.x, base.y, 0)).rotate_local_x(math.radians(45))

        msp.add_line(line1[0], line1[1]).transform(ucs.matrix)
        msp.add_line(line2[0], line2[1]).transform(ucs.matrix)

        dim = msp.add_angular_dim(
            base=base, line1=line1, line2=line2, dimstyle="EZ_ANGULAR"
        )
        dim.render(discard=BRICSCAD, ucs=ucs)

    doc.set_modelspace_vport(height=3 * delta)
    doc.saveas(OUTDIR / f"dim_angular_{dxfversion}_3d.dxf")


if __name__ == "__main__":
    angular_default_above()
    angular_default_center()
    # angular_user_defined_keep_with_line()
    # angular_user_defined_no_leader()
    # angular_user_defined_leader()
    angular_3d()
