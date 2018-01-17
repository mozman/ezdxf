# Copyright 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
import os
import ezdxf
from ezdxf.lldxf.const import versions_supported_by_new


@pytest.fixture(params=versions_supported_by_new)
def drawing(request):
    return ezdxf.new(request.param)


def add_line_entities(entityspace, offset):
    for color in range(1, 256):
        entityspace.add_line((offset+0, color), (offset+50, color), {
            'color': color,
            'layer': u'Träger'
        })


def test_basic_graphics(drawing, tmpdir):
    add_line_entities(drawing.modelspace(), 0)
    add_line_entities(drawing.layout(), 70)
    filename = str(tmpdir.join('basic_graphics_%s.dxf' % drawing.dxfversion))
    try:
        drawing.saveas(filename)
    except ezdxf.DXFError as e:
        pytest.fail("DXFError: {0} for DXF version {1}".format(str(e), drawing.dxfversion))
    assert os.path.exists(filename)
