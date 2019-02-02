# Purpose: using DIMENSION horizontal, vertical and rotated
# Created: 29.12.2018
# Copyright (c) 2018-2019, Manfred Moitzi
# License: MIT License
import pathlib

import ezdxf
from ezdxf.tools.standards import setup_dimstyle
from ezdxf.ezmath import Vector, UCS

OUTDIR = pathlib.Path(r'C:\Users\manfred\Desktop\Outbox')
if not OUTDIR.exists():
    OUTDIR = pathlib.Path()

TEXT_ATTRIBS = {
    'height': .25,
    'style': 'OpenSansCondensed-Light',
}


def to_ocs_angle(ucs, angle):
    # center = Vector()
    angle_vec = Vector.from_deg_angle(angle)
    # center_ocs = ucs.to_ocs(center)
    angel_vec_ocs = ucs.to_ocs(angle_vec)
    end_angle = (angel_vec_ocs - ucs.origin).angle_deg
    return end_angle


def linear_tutorial(dxfversion='R12'):
    dwg = ezdxf.new(dxfversion, setup=True)
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
    dim2 = msp.add_linear_dim(base=(10, 2), ext1=(7, 0), ext2=(10, 0), angle=-30, dimstyle='EZDXF',
                              override={
                                  'dimdle': 0,
                                  'dimtfill': 2,  # custom text fill
                                  'dimtfillclr': 4,  # cyan
                              })
    # Some properties have setter methods for convenience, this is also the reason for not calling dim2.render()
    # automatically.
    dim2.set_arrows(blk=ezdxf.ARROWS.closed_filled, size=.25)
    dim2.set_align(halign='right')
    dim2.render()

    dwg.saveas(OUTDIR / f'dim_linear_{dxfversion}_tutorial.dxf')


def example_background_fill(dxfversion='R12'):
    dwg = ezdxf.new(dxfversion, setup=True)
    msp = dwg.modelspace()
    msp.add_line((0, 2.2), (10, 2.2))

    dim = msp.add_linear_dim(base=(0, 2), ext1=(0, 0), ext2=(3, 0), dimstyle='EZDXF',
                             override={
                                 'dimtfill': 1,  # background color
                             })
    dim.set_text('bgcolor')
    dim.render()

    dim = msp.add_linear_dim(base=(0, 2), ext1=(5, 0), ext2=(8, 0), dimstyle='EZDXF',
                             override={
                                 'dimtfill': 2,  # custom text fill
                                 'dimtfillclr': 4,  # cyan
                             })
    dim.set_text('cyan')
    dim.render()
    dwg.saveas(OUTDIR / f'background_fill_example_{dxfversion}.dxf')


def example_for_all_text_placings_R12():
    dwg = ezdxf.new('R12', setup=True)
    example_for_all_text_placings(dwg, 'dim_linear_text_placing_R12.dxf')


def example_for_all_text_placings_ucs_R12():
    ucs = UCS(origin=(10, 10, 0), ux=(3, 1, 0), uz=(0, 0, 1))
    dwg = ezdxf.new('R12', setup=True)
    example_for_all_text_placings(dwg, 'dim_linear_text_placing_ucs_R12.dxf', ucs)


def example_for_all_text_placings_in_space_R12():
    ucs = UCS(ux=(1, 1, 0), uy=(0, 0, 1))
    dwg = ezdxf.new('R12', setup=True)
    example_for_all_text_placings(dwg, 'dim_linear_text_placing_in_space_R12.dxf', ucs)


def example_for_all_text_placings_R2007():
    dwg = ezdxf.new('R2007', setup=True)
    example_for_all_text_placings(dwg, 'dim_linear_text_placing_R2007.dxf')


def example_for_all_text_placings_ucs_R2007():
    ucs = UCS(origin=(10, 10, 0), ux=(3, 1, 0), uz=(0, 0, 1))
    dwg = ezdxf.new('R2007', setup=True)
    example_for_all_text_placings(dwg, 'dim_linear_text_placing_ucs_R2007.dxf', ucs)


def example_for_all_text_placings_in_space_R2007():
    ucs = UCS(ux=(1, 1, 0), uy=(0, 0, 1))
    dwg = ezdxf.new('R2007', setup=True)
    example_for_all_text_placings(dwg, 'dim_linear_text_placing_in_space_R2007.dxf', ucs)


def example_for_all_text_placings(dwg, filename, ucs=None):
    def add_text(lines, insert):
        attribs = dict(TEXT_ATTRIBS)
        line_space = .4
        delta = Vector(0, line_space, 0)
        if ucs:
            attribs['rotation'] = ucs.to_ocs_angle_deg(0)
            attribs['extrusion'] = ucs.uz

        for line in lines:
            location = ucs.to_ocs(insert) if ucs else insert
            msp.add_text(line, dxfattribs=attribs).set_pos(location)
            insert -= delta

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

    def text(dimstyle, x, y, halign, valign, oblique=0):
        override = {
            'dimdle': 0.,
            'dimexe': .5,  # length of extension line above dimension line
            'dimexo': .5,  # extension line offset
        }
        dimattr = {}
        if oblique:
            dimattr['oblique_angle'] = oblique

        base = (x, y + 2)
        # wide
        dim = msp.add_linear_dim(base=base, ext1=(x, y), ext2=(x + 5, y), dimstyle=dimstyle, override=override,
                                 dxfattribs=dimattr)
        dim.set_align(halign=halign, valign=valign)
        dim.render(ucs=ucs)

        add_text([f'halign={halign}', f'valign={valign}', f'oblique={oblique}'], insert=Vector(x, y))

        # narrow
        dim = msp.add_linear_dim(base=base, ext1=(x + 8, y), ext2=(x + 8.3, y), dimstyle=dimstyle, override=override,
                                 dxfattribs=dimattr)
        dim.set_align(halign=halign, valign=valign)
        dim.render(ucs=ucs)

        # narrow and force text inside
        override['dimtix'] = 1
        dim = msp.add_linear_dim(base=base, ext1=(x + 11, y), ext2=(x + 11.3, y), dimstyle=dimstyle, override=override,
                                 dxfattribs=dimattr)
        dim.set_align(halign=halign, valign=valign)
        dim.render(ucs=ucs)

    def user_text_free(dimstyle, x=0, y=0, leader=False):
        override = {
            'dimdle': 0.,
            'dimexe': .5,  # length of extension line above dimension line
            'dimexo': .5,  # extension line offset
            'dimtfill': 2,  # custom text fill
            'dimtfillclr': 4  # cyan
        }

        base = (x, y + 2)
        dim = msp.add_linear_dim(base=base, ext1=(x, y), ext2=(x + 3, y), dimstyle=dimstyle, override=override)
        location = Vector(x + 3, y + 3, 0)
        dim.set_location(location, leader=leader)
        dim.render(ucs=ucs)
        add_text([f'usr absolute={location}', f'leader={leader}'], insert=Vector(x, y))

        x += 4
        dim = msp.add_linear_dim(base=base, ext1=(x, y), ext2=(x + 3, y), dimstyle=dimstyle, override=override)
        relative = Vector(-1, +1)  # relative to dimline center
        dim.set_location(relative, leader=leader, relative=True)
        dim.render(ucs=ucs)
        add_text([f'usr relative={relative}', f'leader={leader}'], insert=Vector(x, y))

        x += 4
        dim = msp.add_linear_dim(base=base, ext1=(x, y), ext2=(x + 3, y), dimstyle=dimstyle, override=override)
        dh = -.7
        dv = 1.5
        dim.shift_text(dh, dv)
        dim.render(ucs=ucs)
        add_text([f'shift text=({dh}, {dv})', ], insert=Vector(x, y))

        override['dimtix'] = 1  # force text inside
        x += 4
        dim = msp.add_linear_dim(base=base, ext1=(x, y), ext2=(x + .3, y), dimstyle=dimstyle, override=override)
        dh = 0
        dv = 1
        dim.shift_text(dh, dv)
        dim.render(ucs=ucs)
        add_text([f'shift text=({dh}, {dv})', ], insert=Vector(x, y))

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

        user_text_free(dimstyle, x=col * xoffset, y=row * yoffset)
        row += 1

        user_text_free(dimstyle, x=col * xoffset, y=row * yoffset, leader=True)
        row += 1

        text(dimstyle, x=col * xoffset, y=row * yoffset, halign='center', valign='above', oblique=70)
        row += 1

        text(dimstyle, x=col * xoffset, y=row * yoffset, halign='above1', valign='above', oblique=80)
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
    linear_tutorial('R2007')
    example_background_fill('R2007')
    example_for_all_text_placings_R12()
    example_for_all_text_placings_R2007()
    example_for_all_text_placings_ucs_R12()
    example_for_all_text_placings_ucs_R2007()
    example_for_all_text_placings_in_space_R12()
    example_for_all_text_placings_in_space_R2007()

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
