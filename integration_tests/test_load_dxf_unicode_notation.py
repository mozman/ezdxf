#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
import os
import pytest
from ezdxf import recover

BASEDIR = os.path.dirname(__file__)
DATADIR = 'data'


@pytest.fixture(params=['ASCII_R12.dxf'])
def filename(request):
    filename = os.path.join(BASEDIR, DATADIR, request.param)
    if not os.path.exists(filename):
        pytest.skip(f'File {filename} not found.')
    return filename


def test_load_special_dxf_unicode_notation(filename):
    doc, auditor = recover.readfile(filename)
    layer = doc.layers.get('ΛΑΓΕΡÄÜÖ')
    assert layer.dxf.name == 'ΛΑΓΕΡÄÜÖ'

    msp = doc.modelspace()
    lines = msp.query('LINE[layer=="ΛΑΓΕΡÄÜÖ"]')
    assert len(lines) == 2
