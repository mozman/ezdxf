# Purpose: using DIMENSION horizontal, vertical and rotated
# Created: 29.12.2018
# Copyright (c) 2018-2019, Manfred Moitzi
# License: MIT License
import pathlib

import ezdxf
from ezdxf.tools.standards import setup_dimstyle


OUTDIR = pathlib.Path(r'C:\Users\manfred\Desktop\Outbox')
if not OUTDIR.exists():
    OUTDIR = pathlib.Path()


def linear_tutorial_R12():
    dwg = ezdxf.new('R12', setup=True)
    msp = dwg.modelspace()
    msp.add_line((0, 0), (3, 0))

    # horizontal DIMENSION
    # Default DimStyle EZDXF: 1 drawing unit == 1m; scale 1: 100; length_factor=100 -> measurement in cm
    #
    # base: defines the dimension line, ezdxf accepts any point on the dimension line
    # ext1: defines the start point of the first extension line, which also defines the first point to measure
    # ext2: defines the start point of the second extension line, which also defines the second point to measure

    dim = msp.add_linear_dim(base=(3, 2), ext1=(0, 0), ext2=(3, 0), dimstyle='EZDXF', override={'dimtxsty': 'OpenSans'})
    # Necessary second step, to create the BLOCK entity with the DIMENSION geometry.
    # ezdxf supports DXF R2000 attributes for DXF R12 rendering, but they have to be applied by the DIMSTYLE override
    # feature, this additional attributes are not stored in the XDATA section of the DIMENSION entity, they are just
    # used to render the DIMENSION entity.
    # The return value `dim` is not a DIMENSION entity, instead a DimStyleOverride object is returned, the DIMENSION
    # entity is stored as dim.dimension, see also ezdxf.override.DimStyleOverride class.
    dim.render()

    # rotated DIMENSION without `override` uses DEFAULT_DIM_TEXT_STYLE="OPEN_SANS_CONDENSED_LIGHT"
    # angle: defines the angle of the dimension line, measurement is the distance between first and second measurement point
    # in direction of `angle`
    dim2 = msp.add_linear_dim(base=(10, 2), ext1=(7, 0), ext2=(10, 0), angle=-30, dimstyle='EZDXF', override={'dimdle': 0})
    # Some properties have setter methods for convenience, this is also the reason for not calling dim2.render()
    # automatically.
    dim2.set_arrows(blk=ezdxf.ARROWS.closed_filled, size=.25)
    dim2.set_align(halign='right')
    dim2.render()

    dwg.saveas(OUTDIR / 'dim_linear_R12_tutorial.dxf')


def example_for_all_text_placings_R12():
    dwg = ezdxf.new('R12', setup=True)
    example_for_all_text_placings(dwg, 'dim_linear_text_placing_R12.dxf')


def example_for_all_text_placings_R2007():
    dwg = ezdxf.new('R2007', setup=True)
    example_for_all_text_placings(dwg, 'dim_linear_text_placing_R2007.dxf')


def example_for_all_text_placings(dwg, filename):
    msp = dwg.modelspace()
    setup_dimstyle(dwg,
                   name='TICK',
                   fmt='EZ_M_100_H25_CM',
                   )
    setup_dimstyle(dwg,
                   name='ARCHTICK',
                   fmt='EZ_M_100_H25_CM',
                   blk=ezdxf.ARROWS.architectural_tick,
                   )
    setup_dimstyle(dwg,
                   name='CLOSEDBLANK',
                   fmt='EZ_M_100_H25_CM',
                   blk=ezdxf.ARROWS.closed_blank,
                   )

    def text(dimstyle, x, y, halign, valign):
        attribs = {
            'dimdle': 0.,
            'dimexe': .5,  # length of extension line above dimension line
            'dimexo': .5,  # extension line offset
        }
        text_attribs = {
            'height': .25,
            'style': 'OpenSansCondensed-Light',
        }
        base = (x, y + 2)
        # wide
        dim = msp.add_linear_dim(base=base, ext1=(x, y), ext2=(x + 5, y), dimstyle=dimstyle, override=attribs)
        dim.set_align(halign=halign, valign=valign)
        dim.render()

        msp.add_text(f'halign={halign}', dxfattribs=text_attribs).set_pos((x, y))
        msp.add_text(f'valign={valign}', dxfattribs=text_attribs).set_pos((x, y - .4))

        # narrow
        dim = msp.add_linear_dim(base=base, ext1=(x + 8, y), ext2=(x + 8.3, y), dimstyle=dimstyle, override=attribs)
        dim.set_align(halign=halign, valign=valign)
        dim.render()

        # narrow and force text inside
        attribs['dimtix'] = 1
        dim = msp.add_linear_dim(base=base, ext1=(x + 11, y), ext2=(x + 11.3, y), dimstyle=dimstyle, override=attribs)
        dim.set_align(halign=halign, valign=valign)
        dim.render()

    def user_text_fixed(dimstyle, x=0, y=0):
        pass

    def user_text_free(dimstyle, x=0, y=0):
        pass

    def user_text_free_leader(dimstyle, x=0, y=0):
        pass

    dimstyles = ['TICK', 'ARCHTICK', 'CLOSEDBLANK']
    xoffset = 15
    yoffset = 5
    for col, dimstyle in enumerate(dimstyles):
        row = 0
        for halign in ('center', 'left', 'right'):
            text(dimstyle, x=col * xoffset, y=row * yoffset, halign=halign, valign='above')
            row += 1
            text(dimstyle, x=col * xoffset, y=row * yoffset, halign=halign, valign='center')
            row += 1
            text(dimstyle, x=col * xoffset, y=row * yoffset, halign=halign, valign='below')
            row += 1

        text(dimstyle, x=col * xoffset, y=row * yoffset, halign='above1', valign='above')
        row += 1

        text(dimstyle, x=col * xoffset, y=row * yoffset, halign='above2', valign='above')
        row += 1

        user_text_fixed(dimstyle, x=col * xoffset, y=row * yoffset)
        row += 1
        user_text_free(dimstyle, x=col * xoffset, y=row * yoffset)
        row += 1
        user_text_free_leader(dimstyle, x=col * xoffset, y=row * yoffset)
        row += 1

    dwg.saveas(OUTDIR / filename)


def linear_all_arrow_style(version='R12', dimltype=None, dimltex1=None, dimltex2=None, filename=""):
    dwg = ezdxf.new(version, setup=True)
    msp = dwg.modelspace()
    ezdxf_dimstyle = dwg.dimstyles.get('EZDXF')
    ezdxf_dimstyle.copy_to_header(dwg)

    for index, name in enumerate(sorted(ezdxf.ARROWS.__all_arrows__)):
        y = index * 4
        attributes = {
            'dimtxsty': 'LiberationMono',
            'dimdle': 0.5,
        }
        if dimltype:
            attributes['dimltype'] = dimltype
        if dimltex1:
            attributes['dimltex1'] = dimltex1
        if dimltex2:
            attributes['dimltex2'] = dimltex2

        dim = msp.add_linear_dim(base=(3, y + 2), ext1=(0, y), ext2=(3, y), dimstyle='EZDXF', override=attributes)
        dim.set_arrows(blk=name, size=.25)
        dim.render()

    if not filename:
        filename = 'all_arrow_styles_dim_{}.dxf'.format(version)

    dwg.saveas(OUTDIR / filename)


def linear_tutorial_ext_lines():
    dwg = ezdxf.new('R12', setup=True)
    msp = dwg.modelspace()

    msp.add_line((0, 0), (3, 0))

    attributes = {
        'dimexo': 0.5,
        'dimexe': 0.5,
        'dimdle': 0.5,
        'dimblk': ezdxf.ARROWS.none,
        'dimclrt': 3,
    }
    dim = msp.add_linear_dim(base=(3, 2), ext1=(0, 0), ext2=(3, 0), dimstyle='EZDXF', override=attributes)
    dim.render()

    attributes = {
        'dimtad': 4,
        'dimclrd': 2,
        'dimclrt': 4,
    }
    dim = msp.add_linear_dim(base=(10, 2), ext1=(7, 0), ext2=(10, 0), angle=-30, dimstyle='EZDXF', override=attributes)
    dim.render()

    dim = msp.add_linear_dim(base=(3, 5), ext1=(0, 10), ext2=(3, 10), dimstyle='EZDXF', override=attributes)
    dim.render()

    dwg.saveas(OUTDIR / 'dim_linear_R12_ext_lines.dxf')


def linear_EZ_M(fmt):
    dwg = ezdxf.new('R12', setup=True)
    msp = dwg.modelspace()
    ezdxf.setup_dimstyle(dwg, fmt)

    msp.add_line((0, 0), (1, 0))
    dim = msp.add_linear_dim(base=(0, .1), ext1=(0, 0), ext2=(1, 0), dimstyle=fmt)
    dim.render()
    dwg.saveas(OUTDIR / f'dim_linear_R12_{fmt}.dxf')


def linear_EZ_CM(fmt):
    dwg = ezdxf.new('R12', setup=True)
    msp = dwg.modelspace()
    ezdxf.setup_dimstyle(dwg, fmt)

    msp.add_line((0, 0), (100, 0))
    dim = msp.add_linear_dim(base=(0, 10), ext1=(0, 0), ext2=(100, 0), dimstyle=fmt)
    dim.render()
    dwg.saveas(OUTDIR / f'dim_linear_R12_{fmt}.dxf')


def linear_EZ_MM(fmt):
    dwg = ezdxf.new('R12', setup=True)
    msp = dwg.modelspace()
    ezdxf.setup_dimstyle(dwg, fmt)

    msp.add_line((0, 0), (1000, 0))
    dim = msp.add_linear_dim(base=(0, 100), ext1=(0, 0), ext2=(1000, 0), dimstyle=fmt)
    dim.render()
    dwg.saveas(OUTDIR / f'dim_linear_R12_{fmt}.dxf')


ALL = False

if __name__ == '__main__':
    linear_tutorial_R12()
    example_for_all_text_placings_R12()
    example_for_all_text_placings_R2007()
    if ALL:
        linear_all_arrow_style('R12')
        linear_all_arrow_style('R12', dimltex1='DOT2', dimltex2='DOT2', filename='dotted_extension_lines_R12.dxf')
        linear_all_arrow_style('R2000')
        linear_all_arrow_style('R2007', dimltex1='DOT2', dimltex2='DOT2', filename='dotted_extension_lines_R2007.dxf')

        linear_tutorial_ext_lines()

        linear_EZ_M('EZ_M_100_H25_CM')
        linear_EZ_M('EZ_M_1_H25_CM')

        linear_EZ_CM('EZ_CM_100_H25_CM')
        linear_EZ_CM('EZ_CM_1_H25_CM')

        linear_EZ_MM('EZ_MM_100_H25_MM')
        linear_EZ_MM('EZ_MM_1_H25_MM')
