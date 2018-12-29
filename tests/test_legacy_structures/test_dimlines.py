# Copyright (c) 2018 Manfred Moitzi
# License: MIT License

import pytest
import ezdxf
from ezdxf.tools.standards import setup_dimstyles


@pytest.fixture(scope='module')
def dxf12():
    dwg = ezdxf.new('R12')
    setup_dimstyles(dwg)
    return dwg


def test_dimstyle_standard_exist(dxf12):
    assert 'STANDARD' in dxf12.dimstyles


def test_horizontal_dimline(dxf12):
    msp = dxf12.modelspace()
    dimline = msp.add_linear_dim(
        base=(0, 0, 0),
        ext1=(0, 0, 0),
        ext2=(0, 0, 0),
        text_midpoint=(0, 0, 0),
    )
    assert dimline.dxf.dimstyle == 'STANDARD'

    # place to modify dimension or call methods on dimension
    # dimline.set_text('BlaBla')
    msp.render_dimension(dimline)
    block_name = dimline.dxf.geometry
    assert block_name.startswith('*D')

