# Purpose: using ordinate DIMENSION
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

# =======================================================
# Discarding dimension rendering is possible
# for BricsCAD, but is incompatible to AutoCAD -> error
# =======================================================
BRICSCAD = False

DXFVERSION = "R2013"


def add_x_and_y_type(
    msp, feature_location: Vec3, offset: Vec3, rotate: float, override
):
    # Default DimStyle EZDXF:
    # - linear units = 1 drawing unit = 1 m
    # - scale 1:100
    # - closed filled arrow, size = 0.25
    # - text location above dimension line
    #
    # feature_location:
    #   measured location - measurement is the x- or y-distance from the
    #   origin
    # offset:
    #   offset from the feature location to the end of the leader as vector
    # origin:
    #   defines the origin in the render UCS (=WCS by default),
    #   the default origin is (0, 0)
    dim = msp.add_ordinate_x_dim(
        feature_location=feature_location,
        offset=offset,
        rotation=rotate,
        override=override,
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

    # swap x, y axis of the offset for the y-type
    offset = Vec3(offset.y, offset.x)
    msp.add_ordinate_y_dim(
        feature_location=feature_location,
        offset=offset,
        rotation=rotate,
        override=override,
    ).render()


def ordinate_wcs(
    filename: str,
    rotate: float = 0.0,
    override: dict = None,
):
    doc = ezdxf.new(DXFVERSION, setup=True)
    msp = doc.modelspace()
    if override is None:
        override = dict()

    for dimtad, feature_location in [(1, (5, 20)), (0, (0, 0)), (4, (-5, -20))]:
        override["dimtad"] = dimtad
        add_x_and_y_type(
            msp, Vec3(feature_location), Vec3(1, 3), rotate, override
        )
        add_x_and_y_type(
            msp, Vec3(feature_location), Vec3(-1, 3), rotate, override
        )
        add_x_and_y_type(
            msp, Vec3(feature_location), Vec3(1, -3), rotate, override
        )
        add_x_and_y_type(
            msp, Vec3(feature_location), Vec3(-1, -3), rotate, override
        )
    doc.set_modelspace_vport(height=70)
    doc.saveas(OUTDIR / f"{filename}_{DXFVERSION}.dxf")


def ordinate_ucs(
    filename: str,
    rotate: float = 30.0,
):
    doc = ezdxf.new(DXFVERSION, setup=True)
    dimstyle = doc.dimstyles.duplicate_entry("EZDXF", "ORD_CENTER")
    dimstyle.dxf.dimtad = 0
    msp = doc.modelspace()

    for origin in [Vec3(5, 20), Vec3(0, 0), Vec3(-5, -20)]:
        ucs = UCS(origin, ux=Vec3.from_deg_angle(rotate), uz=(0, 0, 1))
        msp.add_ordinate_x_dim(
            feature_location=(3, 2),
            offset=(1, 2),
            dimstyle="ORD_CENTER"
        ).render(ucs=ucs)
        msp.add_ordinate_y_dim(
            feature_location=(3, 2),
            offset=(1, -2),
            dimstyle="ORD_CENTER"
        ).render(ucs=ucs)

    doc.set_modelspace_vport(height=70)
    doc.saveas(OUTDIR / f"{filename}_{DXFVERSION}.dxf")


if __name__ == "__main__":
    ordinate_wcs(filename="ordinate_wcs")
    ordinate_wcs(filename="ordinate_rot_30_deg_wcs", rotate=30)
    ordinate_ucs(filename="ordinate_ucs", rotate=30)
