# Purpose: open a DXF R13 file without plot style name structure setup
# Created: 05.03.2016, 2018 rewritten for pytest
# Copyright (C) 2016-2018, Manfred Moitzi
# License: MIT License
import os
import pytest
import ezdxf


@pytest.fixture(params=["small_r13.dxf", "small_r14.dxf", "no_layouts.dxf"])
def filename(request):
    filename = request.param
    if not os.path.exists(filename):
        filename = os.path.join('integration_tests', filename)
        if not os.path.exists(filename):
            pytest.skip('File {} not found.'.format(filename))
    return filename


def test_open_R13_R14(filename, tmpdir):
    dwg = ezdxf.readfile(filename)
    assert 'Model' in dwg.layouts, 'Model space not found'
    assert 'Layout1' in dwg.layouts, 'Paper space not found'
    msp = dwg.modelspace()
    msp.add_line((0, 0), (10, 3))
    converted = str(tmpdir.join("converted_AC1015.dxf"))
    dwg.saveas(converted)
    assert os.path.exists(converted)