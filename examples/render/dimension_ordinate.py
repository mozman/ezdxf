# Purpose: using ordinate DIMENSION
# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
from typing import Optional
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

DXFVERSION = "R2013"


def add_x_and_y_type(msp, feature_location: Vec3, offset: Vec3, override):
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
        override=override,
    ).render()


def ordinate_wcs(
    filename: str,
    override: dict = None,
):
    doc = ezdxf.new(DXFVERSION, setup=True)
    msp = doc.modelspace()
    if override is None:
        override = dict()

    for dimtad, feature_location in [(1, (5, 20)), (0, (0, 0)), (4, (-5, -20))]:
        override["dimtad"] = dimtad
        add_x_and_y_type(msp, Vec3(feature_location), Vec3(1, 3), override)
    doc.set_modelspace_vport(height=70)
    doc.saveas(OUTDIR / f"{filename}_{DXFVERSION}.dxf")


if __name__ == "__main__":
    ordinate_wcs(filename="ordinate_wcs")
