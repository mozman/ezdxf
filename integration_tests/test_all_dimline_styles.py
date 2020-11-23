# Copyright 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
import os
import random
import ezdxf
from ezdxf.lldxf.const import versions_supported_by_new
from ezdxf.math import Vec3


@pytest.fixture(params=versions_supported_by_new)
def drawing(request):
    return ezdxf.new(request.param, setup=True)


def test_linear_dimline_all_arrow_style(drawing, tmpdir):
    dwg = drawing
    msp = dwg.modelspace()
    ezdxf_dimstyle = dwg.dimstyles.get('EZDXF')
    ezdxf_dimstyle.copy_to_header(dwg)

    for index, name in enumerate(sorted(ezdxf.ARROWS.__all_arrows__)):
        y = index * 4
        attributes = {
            'dimtxsty': 'LiberationMono',
            'dimblk': name,
            'dimtsz': 0.,
            'dimdle': 0.5,
            'dimasz': .25,
        }

        dim = msp.add_linear_dim(base=(3, y + 2), p1=(0, y), p2=(3, y), dimstyle='EZDXF', override=attributes)
        dim.render()

    filename = str(tmpdir.join('all_dimline_styles_{}.dxf'.format(drawing.dxfversion)))
    try:
        drawing.saveas(filename)
    except ezdxf.DXFError as e:
        pytest.fail("DXFError: {0} for DXF version {1}".format(str(e), drawing.dxfversion))
    assert os.path.exists(filename)


def random_point(start, end):
    dist = end - start
    return Vec3(start + random.random() * dist, start + random.random() * dist)


def test_random_multi_point_linear_dimension(tmpdir):
    length = 20
    count = 10
    fname = "multi_random_point_linear_dim_R2007.dxf"

    dwg = ezdxf.new('R2007', setup=True)
    msp = dwg.modelspace()
    points = [random_point(0, length) for _ in range(count)]
    msp.add_lwpolyline(points, dxfattribs={'color': 1})

    # create quick a new DIMSTYLE as alternative to overriding DIMSTYLE attributes
    dimstyle = dwg.dimstyles.duplicate_entry('EZDXF', 'WITHTFILL')

    dimstyle.dxf.dimtfill = 1
    dimstyle.dxf.dimdec = 2

    dimstyle = dwg.dimstyles.duplicate_entry('WITHTFILL', 'WITHTXT')
    dimstyle.dxf.dimblk = ezdxf.ARROWS.closed
    dimstyle.dxf.dimtxsty = 'STANDARD'

    msp.add_multi_point_linear_dim(base=(0, length + 2), points=points, dimstyle='WITHTFILL')
    msp.add_multi_point_linear_dim(base=(-2, 0), points=points, angle=90, dimstyle='WITHTFILL')
    msp.add_multi_point_linear_dim(base=(10, -10), points=points, angle=45, dimstyle='WITHTXT')

    filename = str(tmpdir.join(fname))
    try:
        dwg.saveas(filename)
    except ezdxf.DXFError as e:
        pytest.fail("DXFError: {0} for {1}".format(str(e), fname))
    assert os.path.exists(filename)


def test_draw_all_arrows(drawing, tmpdir):
    msp = drawing.modelspace()
    y = 0
    for index, name in enumerate(sorted(ezdxf.ARROWS.__all_arrows__)):
        if name == "":
            label = '"" = closed filled'
        else:
            label = name
        y = index * 2

        def add_connection_point(p):
            msp.add_circle(p, radius=0.01, dxfattribs={'color': 1})

        msp.add_text(label, {'style': 'OpenSans', 'height': .25}).set_pos((-5, y - .5))
        msp.add_line((-5, y), (-1, y))
        msp.add_line((5, y), (10, y))
        # left side |<- is the reverse orientation
        cp1 = msp.add_arrow(name, insert=(0, y), size=1, rotation=180)
        # right side ->| is the base orientation
        cp2 = msp.add_arrow(name, insert=(4, y), size=1, rotation=0)
        msp.add_line(cp1, cp2)
        add_connection_point(cp1)
        add_connection_point(cp2)

        add_connection_point(msp.add_arrow_blockref(name, insert=(7, y), size=.3, rotation=45))
        add_connection_point(msp.add_arrow_blockref(name, insert=(7.5, y), size=.3, rotation=135))
        add_connection_point(msp.add_arrow_blockref(name, insert=(8, y), size=.5, rotation=-90))

    msp.add_line((0, 0), (0, y))
    msp.add_line((4, 0), (4, y))
    msp.add_line((8, 0), (8, y))

    filename = str(tmpdir.join('draw_all_arrows_{}.dxf'.format(drawing.dxfversion)))
    try:
        drawing.saveas(filename)
    except ezdxf.DXFError as e:
        pytest.fail("DXFError: {0} for DXF version {1}".format(str(e), drawing.dxfversion))
    assert os.path.exists(filename)
