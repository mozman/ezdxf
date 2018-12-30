# Purpose: using DIMENSION horizontal, vertical and rotated
# Created: 29.12.2018
# Copyright (c) 2018-2019, Manfred Moitzi
# License: MIT License
import ezdxf
import pathlib
OUTDIR = pathlib.Path(r'C:\Users\manfred\Desktop\Outbox')


def linear_tutorial():
    dwg = ezdxf.new('R12', setup=True)
    msp = dwg.modelspace()

    msp.add_line((0, 0), (3, 0))

    # horizontal DIMENSION
    # Default DimStyle EZDXF: 1 drawing unit == 1m; scale 1: 100; length_factor=100 -> measurement in cm
    #
    # base: defines the dimension line, ezdxf accepts any point on the dimension line
    # ext1: defines the start point of the first extension line, which also defines the first point to measure
    # ext2: defines the start point of the second extension line, which also defines the second point to measure
    dim = msp.add_linear_dim(base=(3, 2), ext1=(0, 0), ext2=(3, 0), dimstyle='EZDXF')
    # necessary second step, to create the BLOCK entity with the DIMENSION geometry.
    # ezdxf supports DXF R2000 attributes for DXF R12 rendering, but they have to be applied by the DIMSTYLE override
    # feature, this additional attributes are not stored in the DIMSTYLE entity, they are just used to render the DIMENSION
    # entity.
    dxf_r2000_attributes = {
        'dimtxsty': 'OPEN_SANS'  # R12: there is no attribute in DIMSTYLE to store the TEXT style for the measurement text
    }
    msp.render_dimension(dim, override=dxf_r2000_attributes)

    # rotated DIMENSION without `override` uses DEFAULT_DIM_TEXT_STYLE="OPEN_SANS_CONDENSED_LIGHT"
    # angle: defines the angle of the dimension line, measurement is the distance between first and second measurement point
    # in direction of `angle`
    dim2 = msp.add_linear_dim(base=(10, 2), ext1=(7, 0), ext2=(10, 0), angle=-30, dimstyle='EZDXF')
    msp.render_dimension(dim2)

    dwg.saveas(OUTDIR / 'dim_linear_R12_tutorial.dxf')


def linear_EZ_M(fmt):
    dwg = ezdxf.new('R12', setup=True)
    msp = dwg.modelspace()
    ezdxf.setup_dimstyle(dwg, fmt)

    msp.add_line((0, 0), (1, 0))
    dim = msp.add_linear_dim(base=(0, .1), ext1=(0, 0), ext2=(1, 0), dimstyle=fmt)
    msp.render_dimension(dim)
    dwg.saveas(OUTDIR / f'dim_linear_R12_{fmt}.dxf')


def linear_EZ_CM(fmt):
    dwg = ezdxf.new('R12', setup=True)
    msp = dwg.modelspace()
    ezdxf.setup_dimstyle(dwg, fmt)

    msp.add_line((0, 0), (100, 0))
    dim = msp.add_linear_dim(base=(0, 10), ext1=(0, 0), ext2=(100, 0), dimstyle=fmt)
    msp.render_dimension(dim)
    dwg.saveas(OUTDIR / f'dim_linear_R12_{fmt}.dxf')


def linear_EZ_MM(fmt):
    dwg = ezdxf.new('R12', setup=True)
    msp = dwg.modelspace()
    ezdxf.setup_dimstyle(dwg, fmt)

    msp.add_line((0, 0), (1000, 0))
    dim = msp.add_linear_dim(base=(0, 100), ext1=(0, 0), ext2=(1000, 0), dimstyle=fmt)
    msp.render_dimension(dim)
    dwg.saveas(OUTDIR / f'dim_linear_R12_{fmt}.dxf')


if __name__ == '__main__':
    linear_tutorial()

    linear_EZ_M('EZ_M_100_H25_CM')
    linear_EZ_M('EZ_M_50_H25_CM')
    linear_EZ_M('EZ_M_10_H25_CM')
    linear_EZ_M('EZ_M_1_H25_CM')

    linear_EZ_CM('EZ_CM_100_H25_CM')
    linear_EZ_CM('EZ_CM_50_H25_CM')
    linear_EZ_CM('EZ_CM_10_H25_CM')
    linear_EZ_CM('EZ_CM_1_H25_CM')

    linear_EZ_MM('EZ_MM_100_H25_MM')
    linear_EZ_MM('EZ_MM_50_H25_MM')
    linear_EZ_MM('EZ_MM_10_H25_MM')
    linear_EZ_MM('EZ_MM_1_H25_MM')

