#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
import os
import pytest
import ezdxf
BASEDIR = os.path.dirname(__file__)
DATADIR = 'data'


@pytest.fixture(params=['Leica_Disto_S910.dxf'])
def filename(request):
    filename = os.path.join(BASEDIR, DATADIR, request.param)
    if not os.path.exists(filename):
        pytest.skip('File {} not found.'.format(filename))
    return filename


def test_leica_disto_r12(filename):
    dwg = ezdxf.readfile(filename)
    msp = dwg.modelspace()
    points = list(msp.query('POINT'))
    assert len(points) == 11
    assert len(points[0].dxf.location) == 3
