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
BRICSCAD = True


def set_text_style(doc, textstyle=DIM_TEXT_STYLE, name='RADIAL'):
    if doc.dxfversion == 'AC1009':
        return
    dimstyle = doc.dimstyles.get(name)  # type: DimStyle
    dimstyle.dxf.dimtxsty = textstyle


def radial_tutorial(dxfversion='R12'):
    doc = new(dxfversion, setup=True)
    radial_dimstyle = cast('DimStyle', doc.dimstyles.duplicate_entry('EZDXF', 'RADIAL'))
    radial_dimstyle.set_arrows()  # set default 'closed_filled' arrows
    radial_dimstyle.dxf.dimasz = 0.25  # set arrow size

    msp = doc.modelspace()
    msp.add_circle((0, 0), radius=3)

    # radial DIMENSION
    # Default DimStyle EZDXF: 1 drawing unit == 1m; scale 1: 100; length_factor=100 -> measurement in cm
    #
    # center: specifies the center of the circle
    # p1: specifies the measurement point on the circle, which also defines the radius and the orientation (angle) of
    # the dimension line

    dim = msp.add_radius_dim(center=(0, 0), radius=3, angle=45, dimstyle='RADIAL', override={'dimtxsty': 'OpenSans'})
    # Necessary second step, to create the BLOCK entity with the DIMENSION geometry.
    # ezdxf supports DXF R2000 attributes for DXF R12 rendering, but they have to be applied by the DIMSTYLE override
    # feature, this additional attributes are not stored in the XDATA section of the DIMENSION entity, they are just
    # used to render the DIMENSION entity.
    # The return value `dim` is not a DIMENSION entity, instead a DimStyleOverride object is returned, the DIMENSION
    # entity is stored as dim.dimension, see also ezdxf.override.DimStyleOverride class.
    dim.render(discard=BRICSCAD)
    doc.set_modelspace_vport(height=8)
    doc.saveas(OUTDIR / f'dim_radial_{dxfversion}_tutorial.dxf')


if __name__ == '__main__':
    radial_tutorial()
