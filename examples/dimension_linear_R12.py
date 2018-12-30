# Purpose: using DIMENSION horizontal, vertical and rotated
# Created: 29.12.2018
# Copyright (c) 2018-2019, Manfred Moitzi
# License: MIT License

import ezdxf
from ezdxf.tools.standards import setup_dimstyles, setup_styles

dwg = ezdxf.new('R12', setup='all')
setup_styles(dwg)
setup_dimstyles(dwg)
msp = dwg.modelspace()

msp.add_line((0, 0), (3, 0))

# horizontal DIMENSION
# DimStyle EZDXF: 1 drawing unit == 1m; scale 1: 100; length_factor=100 -> measurement in cm
dim = msp.add_linear_dim(base=(3, 2), ext1=(0, 0), ext2=(3, 0), dimstyle='EZDXF')
# necessary second step, to create the BLOCK entity with the DIMENSION geometry.
# ezdxf supports DXF R2000 attributes for DXF R12 rendering, but they have to be applied by the DIMSTYLE override
# feature, this additional attributes are not stored in the DIMSTYLE entity, they are just used to render the DIMENSION
# entity.
dxf_r2000_attributes = {
    'dimtxsty': 'OPEN_SANS'  # R12: there is no attribute in DIMSTYLE to store the TEXT style for the measurement text
}
msp.render_dimension(dim, override=dxf_r2000_attributes)

# horizontal DIMENSION
dim2 = msp.add_linear_dim(base=(10, 2), ext1=(7, 0), ext2=(10, 0), angle=-30, dimstyle='EZDXF')
# necessary second step, to create the BLOCK entity with the DIMENSION geometry
msp.render_dimension(dim2)

dwg.saveas('dimension_linear_R12.dxf')
