# Purpose: using DIMENSION horizontal, vertical and rotated
# Created: 29.12.2018
# Copyright (c) 2018-2019, Manfred Moitzi
# License: MIT License

import ezdxf
from ezdxf.tools.standards import setup_dimstyles, setup_styles

dwg = ezdxf.new('R12')
setup_styles(dwg)
setup_dimstyles(dwg)
msp = dwg.modelspace()

msp.add_line((0, 0), (3, 0))

dimstyle = dwg.dimstyles.new('TEST')
dimstyle.dxf.dimblk = 'EZTICK'
dimstyle.dxf.dimasz = 1
dimstyle.dxf.dimlfac = 100
dimstyle.dxf.dimtxt = .5
dimstyle.dxf.dimgap = .15

# horizontal DIMENSION
dim = msp.add_linear_dim(base=(3, 2), ext1=(0, 0), ext2=(3, 0), dimstyle='TEST')
# necessary second step, to create the BLOCK entity with the DIMENSION geometry
msp.render_dimension(dim, txtstyle='OPEN_SANS')

# horizontal DIMENSION
dim2 = msp.add_linear_dim(base=(10, 2), ext1=(7, 0), ext2=(10, 0), angle=-30, dimstyle='TEST')
# necessary second step, to create the BLOCK entity with the DIMENSION geometry
msp.render_dimension(dim2, txtstyle='OPEN_SANS_CONDENSED_LIGHT')

dwg.saveas('dimension_linear_R12.dxf')
