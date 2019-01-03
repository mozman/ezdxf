# Purpose: using DIMENSION horizontal, vertical and rotated
# Created: 29.12.2018
# Copyright (c) 2018-2019, Manfred Moitzi
# License: MIT License
import ezdxf
import pathlib
from ezdxf.algebra import UCS

OUTDIR = pathlib.Path(r'C:\Users\manfred\Desktop\Outbox')


def linear_3d_example():
    dwg = ezdxf.new('R12', setup=True)
    ucs = UCS((3, 0, 0), ux=(1, 0, 0), uy=(0, 0, 1))
    msp = dwg.modelspace()

    msp.add_line((0, 0), (3, 0))
    dim = msp.add_linear_dim(base=(3, 2), ext1=(0, 0), ext2=(3, 0), dimstyle='EZDXF')
    # necessary second step, to create the BLOCK entity with the DIMENSION geometry.
    msp.render_dimension(dim, ucs=ucs)
    dwg.saveas(OUTDIR / 'dim_linear_3d_R12_example.dxf')


if __name__ == '__main__':
    linear_3d_example()

