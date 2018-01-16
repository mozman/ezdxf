# Purpose: create new drawings for all supported DXF versions and create new
# table entries - check if AutoCAD accepts the new created data structures.
# Created: 20.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
import pytest
import os
import ezdxf
from ezdxf.lldxf.const import versions_supported_by_new


@pytest.fixture(params=versions_supported_by_new)
def drawing(request):
    return ezdxf.new(request.param)


def add_table_entries(dwg):
    dwg.layers.new('MOZMAN-LAYER')
    dwg.styles.new('MOZMAN-STY')
    dwg.linetypes.new('MOZMAN-LTY', {'pattern': [1.0, .5, -.5]})
    dwg.dimstyles.new('MOZMAN-DIMSTY')
    dwg.views.new('MOZMAN-VIEW')
    dwg.viewports.new('MOZMAN-VPORT')
    dwg.ucs.new('MOZMAN-UCS')
    dwg.appids.new('MOZMANAPP')


def test_adding_table_entries(drawing, tmpdir):
    add_table_entries(drawing)
    filename = str(tmpdir.join('table_entries_%s.dxf' % drawing.dxfversion))
    try:
        drawing.saveas(filename)
    except ezdxf.DXFError as e:
        pytest.fail("DXFError: {0} for DXF version {1}".format(str(e), drawing.dxfversion))
    assert os.path.exists(filename)
