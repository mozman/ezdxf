# Copyright 2018, Manfred Moitzi
# License: MIT License
import os
import pytest
import ezdxf


@pytest.fixture(params=['AC1003_LINE_Example.dxf'])
def filename(request):
    filename = request.param
    if not os.path.exists(filename):
        filename = os.path.join('integration_tests', filename)
        if not os.path.exists(filename):
            pytest.skip('File {} not found.'.format(filename))
    return filename


def test_coordinate_order_problem(filename):
    try:
        dwg = ezdxf.readfile(filename, legacy_mode=True)
    except ezdxf.DXFError as e:
        pytest.fail(str(e))
    else:
        msp = dwg.modelspace()
        lines = msp.query('LINE')
        assert lines[0].dxf.start == (1.5, 0, 0)
