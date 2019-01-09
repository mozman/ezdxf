import pytest
import ezdxf
from ezdxf.render.arrows import ARROWS


def test_filled_solid_arrow():
    # special name: no name ""
    assert "" in ARROWS
    ARROWS.is_acad_arrow("")


def test_arrow_name():
    assert ARROWS.arrow_name('_CLOSEDFILLED') == ''
    assert ARROWS.arrow_name('') == ''
    assert ARROWS.arrow_name('_DOTSMALL') == 'DOTSMALL'
    assert ARROWS.arrow_name('_boxBlank') == 'BOXBLANK'
    assert ARROWS.arrow_name('EZ_ARROW') == 'EZ_ARROW'
    assert ARROWS.arrow_name('abcdef') == 'abcdef'


@pytest.fixture(scope='module')
def dxf12():
    return ezdxf.new('R12', setup=True)


@pytest.fixture(scope='module')
def dxf2000():
    return ezdxf.new('R2000', setup=True)


def test_closed_arrow_r12(dxf12):
    blocks = dxf12.blocks
    name = ARROWS.create_block(blocks, ARROWS.closed)
    arrow_entities = list(blocks.get(name))
    assert arrow_entities[0].dxftype() == 'POLYLINE'


def test_closed_arrow_r2000(dxf2000):
    blocks = dxf2000.blocks
    name = ARROWS.create_block(blocks, ARROWS.closed)
    arrow_entities = list(blocks.get(name))
    assert arrow_entities[0].dxftype() == 'LWPOLYLINE'
