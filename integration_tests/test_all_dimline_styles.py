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

        dim = msp.add_linear_dim(base=(3, y+2), ext1=(0, y), ext2=(3, y), dimstyle='EZDXF')

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
