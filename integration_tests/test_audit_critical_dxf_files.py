# Copyright (c) 2018, Manfred Moitzi
# License: MIT License
import pytest
import os
import ezdxf

BASEDIR = 'integration_tests' if os.path.exists('integration_tests') else '.'
DATADIR = 'data'
COLDFIRE = r"D:\Source\dxftest\CADKitSamples\kit-dev-coldfire-xilinx_5213.dxf"


@pytest.mark.skipif(not os.path.exists(COLDFIRE), reason='test data not present')
def test_kit_dev_coldfire():
    dwg = ezdxf.readfile(COLDFIRE)
    auditor = dwg.auditor()
    errors = auditor.run()
    assert len(errors) == 0


@pytest.fixture(params=['Leica_Disto_S910.dxf'])
def filename(request):
    filename = os.path.join(BASEDIR, DATADIR, request.param)
    if not os.path.exists(filename):
        pytest.skip('File {} not found.'.format(filename))
    return filename


def test_leica_disto_r12(filename):
    dwg = ezdxf.readfile(filename, legacy_mode=True)
    auditor = dwg.auditor()
    errors = auditor.run()
    assert len(errors) == 0
