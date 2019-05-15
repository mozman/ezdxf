# Purpose: using DIMENSION horizontal, vertical and rotated
# Created: 29.12.2018
# Copyright (c) 2018-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
import sys
import pathlib
import random
import ezdxf
from ezdxf.tools.standards import setup_dimstyle
from ezdxf.math import Vector, UCS
import logging

if TYPE_CHECKING:
    from ezdxf.eztypes import DimStyle, DimStyleOverride

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


def set_text_style(doc, textstyle=DIM_TEXT_STYLE, name='EZDXF'):
    if doc.dxfversion == 'AC1009':
        return
    dimstyle = doc.dimstyles.get(name)  # type: DimStyle
    dimstyle.dxf.dimtxsty = textstyle


def linear_tutorial(dxfversion='R12'):
    doc = new(dxfversion, setup=True)
    msp = doc.modelspace()
    msp.add_line((0, 0), (3, 0))

    # horizontal DIMENSION
    # Default DimStyle EZDXF: 1 drawing unit == 1m; scale 1: 100; length_factor=100 -> measurement in cm
    #
    # base: defines the dimension line, ezdxf accepts any point on the dimension line
    # p1: defines the start point of the first extension line, which also defines the first point to measure
    # p2: defines the start point of the second extension line, which also defines the second point to measure

    dim = msp.add_linear_dim(base=(3, 2), p1=(0, 0), p2=(3, 0), dimstyle='EZDXF', override={'dimtxsty': 'OpenSans'})
    # Necessary second step, to create the BLOCK entity with the DIMENSION geometry.
    # ezdxf supports DXF R2000 attributes for DXF R12 rendering, but they have to be applied by the DIMSTYLE override
    # feature, this additional attributes are not stored in the XDATA section of the DIMENSION entity, they are just
    # used to render the DIMENSION entity.
    # The return value `dim` is not a DIMENSION entity, instead a DimStyleOverride object is returned, the DIMENSION
    # entity is stored as dim.dimension, see also ezdxf.override.DimStyleOverride class.
    dim.render()

    # rotated DIMENSION without `override` uses ezdxf.options.default_dimension_text_style (OpenSansCondensed-Light)
    # angle: defines the angle of the dimension line in relation to the x-axis of the WCS or UCS, measurement is the
    # distance between first and second measurement point in direction of `angle`
    dim2 = msp.add_linear_dim(base=(10, 2), p1=(7, 0), p2=(10, 0), angle=-30, dimstyle='EZDXF',
                              override={
                                  'dimdle': 0,
                                  'dimdec': 2,
                                  'dimtfill': 2,  # custom text fill
                                  'dimtfillclr': 4,  # cyan
                              })  # type: DimStyleOverride
    # Some properties have setter methods for convenience, this is also the reason for not calling dim2.render()
    # automatically.
    dim2.set_arrows(blk=ezdxf.ARROWS.closed_filled, size=.25)
    dim2.set_text_align(halign='right')
    dim2.render()

    doc.saveas(OUTDIR / f'dim_linear_{dxfversion}_tutorial.dxf')


def example_background_fill(dxfversion='R12'):
    """
    This example shows the background fill feature, ezdxf uses MTEXT for this feature and has no effect in DXF R12.

    """
    doc = new(dxfversion, setup=True)
    msp = doc.modelspace()
    msp.add_line((0, 2.2), (10, 2.2))

    dim = msp.add_linear_dim(base=(0, 2), p1=(0, 0), p2=(3, 0), dimstyle='EZDXF',
                             override={
                                 'dimtfill': 1,  # background color
                             })  # type: DimStyleOverride
    dim.set_text('bgcolor')
    dim.render()

    dim = msp.add_linear_dim(base=(0, 2), p1=(5, 0), p2=(8, 0), dimstyle='EZDXF',
                             override={
                                 'dimtfill': 2,  # custom text fill
                                 'dimtfillclr': 4,  # cyan
                             })  # type: DimStyleOverride
    dim.set_text('cyan')
    dim.render()
    doc.saveas(OUTDIR / f'background_fill_example_{dxfversion}.dxf')


def example_for_all_text_placings_R12():
    doc = new('R12', setup=True)
    example_for_all_text_placings(doc, 'dim_linear_text_placing_R12.dxf')


def example_for_all_text_placings_ucs_R12():
    ucs = UCS(origin=(10, 10, 0), ux=(3, 1, 0), uz=(0, 0, 1))
    doc = new('R12', setup=True)
    example_for_all_text_placings(doc, 'dim_linear_text_placing_ucs_R12.dxf', ucs)


def example_for_all_text_placings_in_space_R12():
    ucs = UCS(ux=(1, 1, 0), uy=(0, 0, 1))
    doc = new('R12', setup=True)
    example_for_all_text_placings(doc, 'dim_linear_text_placing_in_space_R12.dxf', ucs)


def example_for_all_text_placings_R2007():
    doc = new('R2007', setup=True)
    set_text_style(doc)
    example_for_all_text_placings(doc, 'dim_linear_text_placing_R2007.dxf')


def example_for_all_text_placings_ucs_R2007():
    ucs = UCS(origin=(10, 10, 0), ux=(3, 1, 0), uz=(0, 0, 1))
    doc = ezdxf.new('R2007', setup=True)
    set_text_style(doc)
    example_for_all_text_placings(doc, 'dim_linear_text_placing_ucs_R2007.dxf', ucs)


def example_for_all_text_placings_in_space_R2007():
    ucs = UCS(ux=(1, 1, 0), uy=(0, 0, 1))
    doc = new('R2007', setup=True)
    set_text_style(doc)
    example_for_all_text_placings(doc, 'dim_linear_text_placing_in_space_R2007.dxf', ucs)


def example_for_all_text_placings(doc, filename, ucs=None):
    """
    This example shows many combinations of dimension text placing by `halign`, `valign` and user defined location
    override.

    Args:
        doc: DXF drawing
        filename: file name for saving
        ucs: user defined coordinate system

    """
    def add_text(lines, insert):
        insert += (.2, 0)
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

    msp = doc.modelspace()
    setup_dimstyle(doc,
                   name='TICK',
                   fmt='EZ_M_100_H25_CM',
                   style=DIM_TEXT_STYLE,
                   )
    setup_dimstyle(doc,
                   name='ARCHTICK',
                   fmt='EZ_M_100_H25_CM',
                   blk=ezdxf.ARROWS.architectural_tick,
                   style=DIM_TEXT_STYLE,
                   )
    setup_dimstyle(doc,
                   name='CLOSEDBLANK',
                   fmt='EZ_M_100_H25_CM',
                   blk=ezdxf.ARROWS.closed_blank,
                   style=DIM_TEXT_STYLE,
                   )

    def text(dimstyle, x, y, halign, valign, oblique=0):
        """
        Default dimension text placing

        Args:
            dimstyle: dimstyle to use
            x: start point x
            y: start point y
            halign: horizontal text alignment - `left`, `right`, `center`, `above1`, `above2`, requires DXF R2000+
            valign: vertical text alignment `above`, `center`, `below`
            oblique: angle of oblique extension line, 0 = orthogonal to dimension line

        """
        dimattr = {}
        if oblique:
            dimattr['oblique_angle'] = oblique

        base = (x, y + 2)
        # wide
        dim = msp.add_linear_dim(base=base, p1=(x, y), p2=(x + 5, y), dimstyle=dimstyle,
                                 dxfattribs=dimattr)  # type: DimStyleOverride
        dim.set_text_align(halign=halign, valign=valign)
        dim.render(ucs=ucs, discard=BRICSCAD)

        add_text([f'halign={halign}', f'valign={valign}', f'oblique={oblique}'], insert=Vector(x, y))

        # narrow
        dim = msp.add_linear_dim(base=base, p1=(x + 7, y), p2=(x + 7.3, y), dimstyle=dimstyle,
                                 dxfattribs=dimattr)  # type: DimStyleOverride
        dim.set_text_align(halign=halign, valign=valign)
        dim.render(ucs=ucs, discard=BRICSCAD)

        # arrows inside, text outside

        dim = msp.add_linear_dim(base=base, p1=(x + 10, y), p2=(x + 10.9999, y), dimstyle=dimstyle,
                                 override={'dimdec': 2},
                                 dxfattribs=dimattr)  # type: DimStyleOverride
        dim.set_text_align(halign=halign, valign=valign)
        dim.render(ucs=ucs, discard=BRICSCAD)

        # narrow and force text inside
        dim = msp.add_linear_dim(base=base, p1=(x + 14, y), p2=(x + 14.3, y), dimstyle=dimstyle,
                                 override={'dimtix': 1},
                                 dxfattribs=dimattr)  # type: DimStyleOverride
        dim.set_text_align(halign=halign, valign=valign)
        dim.render(ucs=ucs, discard=BRICSCAD)

    def user_text_free(dimstyle, x=0, y=0, leader=False):
        """
        User defined dimension text placing.

        Args:
            dimstyle: dimstyle to use
            x: start point x
            y: start point y
            leader: use leader line if True

        """
        override = {
            'dimdle': 0.,
            'dimexe': .5,  # length of extension line above dimension line
            'dimexo': .5,  # extension line offset
            'dimtfill': 2,  # custom text fill
            'dimtfillclr': 4  # cyan
        }

        base = (x, y + 2)
        dim = msp.add_linear_dim(base=base, p1=(x, y), p2=(x + 3, y), dimstyle=dimstyle,
                                 override=override)  # type: DimStyleOverride
        location = Vector(x + 3, y + 3, 0)
        dim.set_location(location, leader=leader)
        dim.render(ucs=ucs, discard=BRICSCAD)
        add_text([f'usr absolute={location}', f'leader={leader}'], insert=Vector(x, y))

        x += 4
        dim = msp.add_linear_dim(base=base, p1=(x, y), p2=(x + 3, y), dimstyle=dimstyle,
                                 override=override)  # type: DimStyleOverride
        relative = Vector(-1, +1)  # relative to dimline center
        dim.set_location(relative, leader=leader, relative=True)
        dim.render(ucs=ucs, discard=BRICSCAD)
        add_text([f'usr relative={relative}', f'leader={leader}'], insert=Vector(x, y))

        x += 4
        dim = msp.add_linear_dim(base=base, p1=(x, y), p2=(x + 3, y), dimstyle=dimstyle,
                                 override=override)  # type: DimStyleOverride
        dh = -.7
        dv = 1.5
        dim.shift_text(dh, dv)
        dim.render(ucs=ucs, discard=BRICSCAD)
        add_text([f'shift text=({dh}, {dv})', ], insert=Vector(x, y))

        override['dimtix'] = 1  # force text inside
        x += 4
        dim = msp.add_linear_dim(base=base, p1=(x, y), p2=(x + .3, y), dimstyle=dimstyle,
                                 override=override)  # type: DimStyleOverride
        dh = 0
        dv = 1
        dim.shift_text(dh, dv)
        dim.render(ucs=ucs, discard=BRICSCAD)
        add_text([f'shift text=({dh}, {dv})', ], insert=Vector(x, y))

    dimstyles = ['TICK', 'ARCHTICK', 'CLOSEDBLANK']
    xoffset = 17
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

    doc.saveas(OUTDIR / filename)


def example_multi_point_linear_dimension():
    """
    Example for using the ezdxf "multi-point linear dimension" feature, which generates dimension entities for multiple
    points at ones and tries to move dimension text to a readable location.

    This feature works best with DXF R2007+.

    """
    doc = new('R2007', setup=True)
    msp = doc.modelspace()
    points = [(0, 0), (5, 1), (5.2, 1), (5.4, 0), (7, 0), (10, 3)]
    msp.add_lwpolyline(points)

    # create quick a new DIMSTYLE as alternative to overriding DIMSTYLE attributes
    dimstyle = doc.dimstyles.duplicate_entry('EZDXF', 'WITHTFILL')  # type: DimStyle
    dimstyle.dxf.dimtfill = 1

    msp.add_multi_point_linear_dim(base=(0, 5), points=points, dimstyle='WITHTFILL')
    doc.saveas(OUTDIR / f'multi_point_linear_dim_R2007.dxf')


def random_point(start, end):
    dist = end - start
    return Vector(start + random.random() * dist, start + random.random() * dist)


def example_random_multi_point_linear_dimension(count=10, length=20, discard=BRICSCAD):
    """
    Example for using the ezdxf "multi-point linear dimension" feature, which generates dimension entities for multiple
    points at ones and tries to move dimension text to a readable location.

    This feature works best with DXF R2007+.

    """
    doc = new('R2007', setup=True)
    msp = doc.modelspace()

    # create a random polyline.
    points = [random_point(0, length) for _ in range(count)]
    msp.add_lwpolyline(points, dxfattribs={'color': 1})

    # create quick a new DIMSTYLE as alternative to overriding DIMSTYLE attributes
    dimstyle = doc.dimstyles.duplicate_entry('EZDXF', 'WITHTFILL')  # type: DimStyle

    dimstyle.dxf.dimtfill = 1
    dimstyle.dxf.dimdec = 2

    dimstyle = doc.dimstyles.duplicate_entry('WITHTFILL', 'WITHTXT')  # type: DimStyle
    dimstyle.dxf.dimblk = ezdxf.ARROWS.closed
    dimstyle.dxf.dimtxsty = 'STANDARD'
    dimstyle.dxf.dimrnd = .5
    dimstyle.set_text_align(valign='center')

    msp.add_multi_point_linear_dim(base=(0, length + 2), points=points, dimstyle='WITHTFILL', discard=discard)
    msp.add_multi_point_linear_dim(base=(-2, 0), points=points, angle=90, dimstyle='WITHTFILL', discard=discard)
    msp.add_multi_point_linear_dim(base=(10, -10), points=points, angle=45, dimstyle='WITHTXT', discard=discard)
    doc.saveas(OUTDIR / f'multi_random_point_linear_dim_R2007.dxf')


def linear_all_arrow_style(version='R12', dimltype=None, dimltex1=None, dimltex2=None, filename=""):
    """
    Show all AutoCAD standard arrows on a linear dimension.

    Args:
        version: DXF version
        dimltype: dimension linetype
        dimltex1: linetype for first extension line
        dimltex2: linetype for second extension line
        filename: filename for saving

    """
    doc = new(version, setup=True)
    msp = doc.modelspace()
    ezdxf_dimstyle = doc.dimstyles.get('EZDXF')  # type: DimStyle
    ezdxf_dimstyle.copy_to_header(doc)

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

        dim = msp.add_linear_dim(base=(3, y + 2), p1=(0, y), p2=(3, y), dimstyle='EZDXF',
                                 override=attributes)  # type: DimStyleOverride
        dim.set_arrows(blk=name, size=.25)
        dim.render()

    if not filename:
        filename = 'all_arrow_styles_dim_{}.dxf'.format(version)

    doc.saveas(OUTDIR / filename)


def linear_tutorial_using_tolerances(version='R2000'):
    """
    Shows usage of tolerances for the dimension text.

    ezdxf uses MTEXT features for tolerance rendering and therefore requires DXF R2000+, but if you are using a
    friendly CAD application like BricsCAD, you can let the CAD application do the rendering job, be aware this files
    are not AutoCAD compatible.

    Args:
        version: DXF version

    """
    doc = new(version, setup=True)
    msp = doc.modelspace()

    # DO NOT RENDER BY EZDXF for DXF R12
    discard = version == 'R12'

    tol_style = doc.dimstyles.duplicate_entry('EZDXF', 'TOLERANCE')  # type: DimStyle
    # not all features are supported by DXF R12:
    # zero suppression (DIMTZIN), align (DIMTOLJ) and dec (DIMTDEC) require DXF R2000+
    tol_style.set_tolerance(.1, hfactor=.5, align="top", dec=2)
    msp.add_linear_dim(base=(0, 3), p1=(0, 0), p2=(10, 0), dimstyle='tolerance').render(discard=discard)

    dim = msp.add_linear_dim(base=(0, 3), p1=(15, 0), p2=(15.5, 0), dimstyle='tolerance')
    # set tolerance attributes by dim style override
    dim.set_tolerance(.1, .15, hfactor=.4, align="middle", dec=2)
    dim.render(discard=discard)

    doc.saveas(OUTDIR / f'dimensions_with_tolerance_{version}.dxf')


def linear_tutorial_using_limits(version='R2000'):
    """
    Shows usage of limits for the dimension text, limits are the lower and upper limit for the measured distance, the
    measurement itself is not shown.

    ezdxf uses MTEXT features for limits rendering and therefore requires DXF R2000+, but if you are using a
    friendly CAD application like BricsCAD, you can let the CAD application do the rendering job, be aware this files
    are not AutoCAD compatible.

    Args:
        version: DXF version

    """
    doc = new(version, setup=True)
    msp = doc.modelspace()
    # DO NOT RENDER BY EZDXF for DXF R12
    discard = version == 'R12'

    tol_style = doc.dimstyles.duplicate_entry('EZDXF', 'LIMITS')  # type: DimStyle

    # not all features are supported by DXF R12:
    # zero suppression (DIMTZIN), align (DIMTOLJ) and dec (DIMTDEC) require DXF R2000+
    tol_style.set_limits(upper=.1, lower=.1, hfactor=.5, dec=2)

    msp.add_linear_dim(base=(0, 3), p1=(0, 0), p2=(10, 0), dimstyle='limits').render(discard=discard)
    msp.add_linear_dim(base=(0, 3), p1=(15, 0), p2=(15.5, 0), dimstyle='limits').render(discard=discard)
    doc.saveas(OUTDIR / f'dimensions_with_limits_{version}.dxf')


def linear_tutorial_using_tvp():
    """
    For the vertical text alignment `center`, exists an additional DXF feature, to move the dimension text vertical
    up and down (DIMTVP). Vertical distance dimension line to text center =  text_height * vshift (DIMTVP)

    """
    doc = new('R2000', setup=True)
    msp = doc.modelspace()
    style = doc.dimstyles.duplicate_entry('EZDXF', 'TVP')  # type: DimStyle
    # shift text upwards
    style.set_text_align(valign='center', vshift=2.0)
    msp.add_linear_dim(base=(0, 3), p1=(0, 0), p2=(10, 0), dimstyle='TVP').render()
    msp.add_linear_dim(base=(0, 3), p1=(15, 0), p2=(15.5, 0), dimstyle='TVP').render()

    style = doc.dimstyles.duplicate_entry('EZDXF', 'TVP2')  # type: DimStyle
    # shift text downwards
    style.set_text_align(valign='center', vshift=-2.0)
    msp.add_linear_dim(base=(0, 7), p1=(0, 5), p2=(10, 5), dimstyle='TVP2').render()
    msp.add_linear_dim(base=(0, 7), p1=(15, 5), p2=(15.5, 5), dimstyle='TVP2').render()

    doc.saveas(OUTDIR / 'dimensions_with_dimtvp.dxf')


def linear_tutorial_ext_lines():
    doc = new('R12', setup=True)
    msp = doc.modelspace()

    msp.add_line((0, 0), (3, 0))

    attributes = {
        'dimexo': 0.5,
        'dimexe': 0.5,
        'dimdle': 0.5,
        'dimblk': ezdxf.ARROWS.none,
        'dimclrt': 3,
    }
    msp.add_linear_dim(base=(3, 2), p1=(0, 0), p2=(3, 0), dimstyle='EZDXF', override=attributes).render()

    attributes = {
        'dimtad': 4,
        'dimclrd': 2,
        'dimclrt': 4,
    }
    msp.add_linear_dim(base=(10, 2), p1=(7, 0), p2=(10, 0), angle=-30, dimstyle='EZDXF', override=attributes).render()
    msp.add_linear_dim(base=(3, 5), p1=(0, 10), p2=(3, 10), dimstyle='EZDXF', override=attributes).render()
    doc.saveas(OUTDIR / 'dim_linear_R12_ext_lines.dxf')


def linear_EZ_M(fmt):
    doc = new('R12', setup=('linetypes', 'styles'))
    msp = doc.modelspace()
    ezdxf.setup_dimstyle(doc, fmt)

    msp.add_line((0, 0), (1, 0))
    msp.add_linear_dim(base=(0, 1), p1=(0, 0), p2=(1, 0), dimstyle=fmt).render()
    doc.saveas(OUTDIR / f'dim_linear_R12_{fmt}.dxf')


def linear_EZ_CM(fmt):
    doc = new('R12', setup=('linetypes', 'styles'))
    msp = doc.modelspace()
    ezdxf.setup_dimstyle(doc, fmt)

    msp.add_line((0, 0), (100, 0))
    msp.add_linear_dim(base=(0, 100), p1=(0, 0), p2=(100, 0), dimstyle=fmt).render()
    doc.saveas(OUTDIR / f'dim_linear_R12_{fmt}.dxf')


def linear_EZ_MM(fmt):
    doc = new('R12', setup=('linetypes', 'styles'))
    msp = doc.modelspace()
    ezdxf.setup_dimstyle(doc, fmt)

    msp.add_line((0, 0), (1000, 0))
    msp.add_linear_dim(base=(0, 1000), p1=(0, 0), p2=(1000, 0), dimstyle=fmt).render()
    doc.saveas(OUTDIR / f'dim_linear_R12_{fmt}.dxf')


ALL = False

if __name__ == '__main__':
    linear_tutorial_using_tvp()
    linear_tutorial_using_limits('R2000')
    linear_tutorial_using_limits('R12')
    linear_tutorial_using_tolerances('R2000')
    linear_tutorial_using_tolerances('R12')
    example_for_all_text_placings_ucs_R2007()

    if ALL:
        linear_tutorial('R2007')
        linear_tutorial('R12')
        example_background_fill('R2007')
        example_for_all_text_placings_R12()
        example_for_all_text_placings_R2007()

        example_multi_point_linear_dimension()
        example_random_multi_point_linear_dimension(count=10, length=20)

        example_for_all_text_placings_ucs_R12()
        example_for_all_text_placings_in_space_R12()
        example_for_all_text_placings_in_space_R2007()

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
