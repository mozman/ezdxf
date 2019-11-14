# Purpose: using radial DIMENSION
# Created: 10.11.2018
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, cast
import sys
import pathlib
import random
import ezdxf
from ezdxf.tools.standards import setup_dimstyle
from ezdxf.math import Vector, UCS
from ezdxf.render.arrows import ARROWS
import logging

if TYPE_CHECKING:
    from ezdxf.eztypes import DimStyle, DimStyleOverride, Drawing

new = ezdxf.new

# ========================================
# IMPORTANT:
# this script uses f-strings (Python 3.6)
# ========================================
if sys.version_info < (3, 6):
    print("This script requires Python 3.6 (f-strings)")
    sys.exit()

# ========================================
# Setup logging
# ========================================
logging.basicConfig(level='WARNING')

# ========================================
# Setup your preferred output directory
# ========================================
OUTDIR = pathlib.Path(r'C:\Users\manfred\Desktop\Outbox')
if not OUTDIR.exists():
    OUTDIR = pathlib.Path()

# ========================================
# Default text attributes
# ========================================
TEXT_ATTRIBS = {
    'height': .25,
    'style': ezdxf.options.default_dimension_text_style,
}
DIM_TEXT_STYLE = ezdxf.options.default_dimension_text_style

# =======================================================
# Discarding dimension rendering is possible
# for BricsCAD, but is incompatible to AutoCAD -> error
# =======================================================
BRICSCAD = False


def set_text_style(doc, textstyle=DIM_TEXT_STYLE, name='RADIAL'):
    if doc.dxfversion == 'AC1009':
        return
    dimstyle = doc.dimstyles.get(name)  # type: DimStyle
    dimstyle.dxf.dimtxsty = textstyle


def create_radial_dimstyle(doc):
    radial_dimstyle = cast('DimStyle', doc.dimstyles.duplicate_entry('EZDXF', 'RADIAL'))
    radial_dimstyle.set_arrows(blk=ARROWS.closed_blank)  # default closed filled arrow
    radial_dimstyle.dxf.dimasz = 0.25  # set arrow size
    return radial_dimstyle


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


def radial_default_outside(dxfversion='R2000', delta=10):
    doc = new(dxfversion, setup=True)
    create_radial_dimstyle(doc)
    msp = doc.modelspace()
    for x, y in multiple_locations(delta=delta):
        angle = Vector(x, y).angle_deg
        msp.add_circle((x, y), radius=3)

        # radial DIMENSION
        # Default DimStyle RADIAL: 1 drawing unit == 1m; scale 1: 100; length_factor=100 -> measurement in cm
        #
        # center: specifies the center of the circle
        # radius: specifies the radius of the circle
        # angle: specifies the the orientation (angle) of the dimension line
        dim = msp.add_radius_dim(center=(x, y), radius=3, angle=angle, dimstyle='RADIAL',
                                 override={'dimtxsty': 'OpenSans'})

        # Necessary second step, to create the BLOCK entity with the DIMENSION geometry.
        # ezdxf supports DXF R2000 attributes for DXF R12 rendering, but they have to be applied by the DIMSTYLE override
        # feature, this additional attributes are not stored in the XDATA section of the DIMENSION entity, they are just
        # used to render the DIMENSION entity.
        # The return value `dim` is not a DIMENSION entity, instead a DimStyleOverride object is returned, the DIMENSION
        # entity is stored as dim.dimension, see also ezdxf.override.DimStyleOverride class.
        dim.render(discard=BRICSCAD)
    doc.set_modelspace_vport(height=3 * delta)
    doc.saveas(OUTDIR / f'dim_radial_{dxfversion}_default_outside.dxf')


def radial_default_inside(dxfversion='R2000', delta=10):
    doc = new(dxfversion, setup=True)
    dimstyle = create_radial_dimstyle(doc)
    # force dim text inside?
    dimstyle.dxf.dimtix = 1  # force text inside
    dimstyle.dxf.dimatfit = 0  # force text inside
    msp = doc.modelspace()
    for x, y in multiple_locations(delta=delta):
        angle = Vector(x, y).angle_deg
        msp.add_circle((x, y), radius=3)

        dim = msp.add_radius_dim(center=(x, y), radius=3, angle=angle, dimstyle='RADIAL',
                                 override={'dimtxsty': 'OpenSans'})
        dim.render(discard=BRICSCAD)
    doc.set_modelspace_vport(height=3 * delta)
    doc.saveas(OUTDIR / f'dim_radial_{dxfversion}_default_inside.dxf')


def radial_default_outside_horizontal(dxfversion='R2000', delta=10):
    doc = new(dxfversion, setup=True)
    dimstyle = create_radial_dimstyle(doc)
    # force dim text inside?
    dimstyle.dxf.dimtoh = 1  # force text outside horizontal
    msp = doc.modelspace()
    for x, y in multiple_locations(delta=delta):
        angle = Vector(x, y).angle_deg
        msp.add_circle((x, y), radius=3)

        dim = msp.add_radius_dim(center=(x, y), radius=3, angle=angle, dimstyle='RADIAL',
                                 override={'dimtxsty': 'OpenSans'})
        dim.render(discard=BRICSCAD)
    doc.set_modelspace_vport(height=3 * delta)
    doc.saveas(OUTDIR / f'dim_radial_{dxfversion}_default_outside_horizontal.dxf')


def radial_default_inside_horizontal(dxfversion='R2000', delta=10):
    doc = new(dxfversion, setup=True)
    dimstyle = create_radial_dimstyle(doc)
    # force dim text inside?
    dimstyle.dxf.dimtix = 1  # force text inside
    dimstyle.dxf.dimatfit = 0  # force text inside
    dimstyle.dxf.dimtih = 1  # force text inside horizontal
    msp = doc.modelspace()
    for x, y in multiple_locations(delta=delta):
        angle = Vector(x, y).angle_deg
        msp.add_circle((x, y), radius=3)

        dim = msp.add_radius_dim(center=(x, y), radius=3, angle=angle, dimstyle='RADIAL',
                                 override={'dimtxsty': 'OpenSans'})
        dim.render(discard=BRICSCAD)
    doc.set_modelspace_vport(height=3 * delta)
    doc.saveas(OUTDIR / f'dim_radial_{dxfversion}_default_inside_horizontal.dxf')


if __name__ == '__main__':
    radial_default_outside()
    radial_default_inside()
    radial_default_outside_horizontal()
    radial_default_inside_horizontal()