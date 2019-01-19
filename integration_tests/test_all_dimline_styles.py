# Copyright 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
import os
import ezdxf
from ezdxf.lldxf.const import versions_supported_by_new


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

        dim = msp.add_linear_dim(base=(3, y + 2), ext1=(0, y), ext2=(3, y), dimstyle='EZDXF')

        attributes = {
            'dimtxsty': 'LiberationMono',
            'dimblk': name,
            'dimtsz': 0.,
            'dimdle': 0.5,
            'dimasz': .25,
        }
        style = dim.dimstyle_override(attributes)
        msp.render_dimension(dim, override=style)

    filename = str(tmpdir.join('all_dimline_styles_{}.dxf'.format(drawing.dxfversion)))
    try:
        drawing.saveas(filename)
    except ezdxf.DXFError as e:
        pytest.fail("DXFError: {0} for DXF version {1}".format(str(e), drawing.dxfversion))
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
