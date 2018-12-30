# Copyright (c) 2018 Manfred Moitzi
# License: MIT License

import pytest
import ezdxf
from ezdxf.render.dimension import DimStyleOverride, DXFAttributeError


@pytest.fixture(scope='module')
def dxf12():
    dwg = ezdxf.new('R12', setup='all')
    return dwg


def test_dimstyle_standard_exist(dxf12):
    assert 'EZDXF' in dxf12.dimstyles


def test_dimstyle_override(dxf12):
    override_sttribute = {
        'dimtxsty': 'TEST',
        'invalid': 'invalid',
    }
    dimstyle = dxf12.dimstyles.get('EZDXF')
    override = DimStyleOverride(dimstyle, override_sttribute)
    assert override.get('dimtxsty') == 'TEST'
    with pytest.raises(DXFAttributeError):
        _ = override.get('invalid')


def test_horizontal_dimline(dxf12):
    msp = dxf12.modelspace()
    dimline = msp.add_linear_dim(
        base=(3, 2, 0),
        ext1=(0, 0, 0),
        ext2=(3, 0, 0),

    )
    assert dimline.dxf.dimstyle == 'EZDXF'

    msp.render_dimension(dimline)
    block_name = dimline.dxf.geometry
    assert block_name.startswith('*D')

    block = dxf12.blocks.get(block_name)
    assert len(list(block.query('TEXT'))) == 1
    assert len(list(block.query('INSERT'))) == 2  # ticks
    assert len(list(block.query('LINE'))) == 3  # dimension line + 2 extension lines
    assert len(list(block.query('POINT'))) == 3  # def points


