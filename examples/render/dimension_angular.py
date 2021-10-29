# Purpose: using angular DIMENSION
# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
import pathlib
import math
import ezdxf
from ezdxf.math import Vec3, UCS, NULLVEC
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


def locations():
    def location(offset: Vec3, flip: float):
        base = Vec3(0, 5) + offset
        p1 = Vec3(-4, 3 * flip) + offset
        p2 = Vec3(-1, 0) + offset
        p4 = Vec3(4, 3 * flip) + offset
        p3 = Vec3(1, 0) + offset
        return base, (p1, p2), (p3, p4)

    return [
        location(NULLVEC, +1),
        location(Vec3(10, 0), -1),
    ]


def angular_2l_default_above(dxfversion="R2000"):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    for base, line1, line2 in locations():
        msp.add_line(line1[0], line1[1])
        msp.add_line(line2[0], line2[1])

        # Default DimStyle EZ_CURVED:
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
        dim = msp.add_angular_dim_2l(
            base=base, line1=line1, line2=line2, dimstyle="EZ_CURVED"
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
    doc.set_modelspace_vport(height=30)
    doc.saveas(OUTDIR / f"dim_angular_2l_{dxfversion}_default_above.dxf")


def add_lines(
    msp, center: Vec3, radius: float, start_angle: float, end_angle: float
):
    start_point = center + Vec3.from_deg_angle(start_angle) * radius
    end_point = center + Vec3.from_deg_angle(end_angle) * radius
    msp.add_line(center, start_point)
    msp.add_line(center, end_point)


def angular_cra_default_above(dxfversion="R2013"):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    radius = 5
    distance = 2
    data = [
        [Vec3(0, 0), 60, 120],
        [Vec3(10, 0), 300, 240],
        [Vec3(20, 0), 240, 300],
    ]
    for center, start_angle, end_angle in data:
        add_lines(msp, center, radius, start_angle, end_angle)
        # Default DimStyle EZ_CURVED:
        # - angle units = degree
        # - scale 1: 100
        # - closed filled arrow, size = 0.25
        # - text location above dimension line
        #
        # center:
        #   center of angle
        # radius:
        #   distance from center to the start of the extension lines
        # distance:
        #   distance from start of the extension lines to the dimension line
        # start_angle:
        #   start angle in degrees
        # end_angle:
        #   end angle in degrees
        # The measurement is always done from start_angle to end_angle in
        # counter clockwise orientation. This does not always match the result
        # in CAD applications!
        dim = msp.add_angular_dim_cra(
            center, radius, start_angle, end_angle, distance
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

    doc.set_modelspace_vport(height=30)
    doc.saveas(OUTDIR / f"dim_angular_cra_{dxfversion}_default_above.dxf")


def angular_cra_default_center(dxfversion="R2000"):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    radius = 5
    distance = 2
    data = [
        [Vec3(0, 0), 60, 120],
        [Vec3(10, 0), 300, 240],
        [Vec3(20, 0), 240, 300],
    ]
    for center, start_angle, end_angle in data:
        add_lines(msp, center, radius, start_angle, end_angle)
        dim = msp.add_angular_dim_cra(
            center,
            radius,
            start_angle,
            end_angle,
            distance,
            dimstyle="EZ_CURVED",
            override={"dimtad": 0},
        )
        dim.render(discard=BRICSCAD)
    doc.set_modelspace_vport(height=30)
    doc.saveas(OUTDIR / f"dim_angular_cra_{dxfversion}_default_center.dxf")


def angular_3d(dxfversion="R2000"):
    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()

    for base, line1, line2 in locations():
        ucs = UCS(origin=(base.x, base.y, 0)).rotate_local_x(math.radians(45))

        msp.add_line(line1[0], line1[1]).transform(ucs.matrix)
        msp.add_line(line2[0], line2[1]).transform(ucs.matrix)

        dim = msp.add_angular_dim_2l(
            base=base, line1=line1, line2=line2, dimstyle="EZ_CURVED"
        )
        dim.render(discard=BRICSCAD, ucs=ucs)

    doc.set_modelspace_vport(height=30)
    doc.saveas(OUTDIR / f"dim_angular_{dxfversion}_3d.dxf")


if __name__ == "__main__":
    angular_cra_default_above()
    angular_cra_default_center()
    angular_3d()
