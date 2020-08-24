# Copyright (c) 2018-2020, Manfred Moitzi
# License: MIT License
import os
import pytest
import ezdxf
from ezdxf import recover

BASEDIR = 'integration_tests' if os.path.exists('integration_tests') else '.'
DATADIR = 'data'


@pytest.fixture(params=['AC1003_LINE_Example.dxf'])
def filename(request):
    filename = os.path.join(BASEDIR, DATADIR, request.param)
    if not os.path.exists(filename):
        pytest.skip('File {} not found.'.format(filename))
    return filename


def test_coordinate_order_problem(filename):
    try:
        doc, auditor = recover.auto_readfile(filename)
    except ezdxf.DXFError as e:
        pytest.fail(str(e))
    else:
        msp = doc.modelspace()
        lines = msp.query('LINE')
        assert lines[0].dxf.start == (1.5, 0, 0)
