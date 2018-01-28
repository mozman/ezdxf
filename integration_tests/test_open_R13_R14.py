# Copyright 2018, Manfred Moitzi
# License: MIT License
import os
import pytest
import ezdxf


BASEDIR = 'integration_tests' if os.path.exists('integration_tests') else '.'
DATADIR = 'data'


@pytest.fixture(params=["small_r13.dxf", "small_r14.dxf", "no_layouts.dxf"])
def filename(request):
    filename = os.path.join(BASEDIR, DATADIR, request.param)
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
