# Copyright (c) 2018-2019, Manfred Moitzi
# License: MIT License
import os
import pytest
import ezdxf
BASEDIR = 'integration_tests' if os.path.exists('integration_tests') else '.'
DATADIR = 'data'


@pytest.fixture(params=['Leica_Disto_S910.dxf'])
def filename(request):
    filename = os.path.join(BASEDIR, DATADIR, request.param)
    if not os.path.exists(filename):
        pytest.skip('File {} not found.'.format(filename))
    return filename


def test_leica_disto_r12(filename):
    # new entity system: legacy mode not necessary
    dwg = ezdxf.readfile(filename, legacy_mode=False)
    msp = dwg.modelspace()
    points = list(msp.query('POINT'))
    assert len(points) == 11
    assert len(points[0].dxf.location) == 3
