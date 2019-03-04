# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
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


def test_closed_arrow_doc_r12():
    doc = ezdxf.new2(dxfversion='R12', setup=True)
    blocks = doc.blocks
    name = ARROWS.create_block(blocks, ARROWS.closed)
    arrow_entities = list(blocks.get(name))
    assert arrow_entities[0].dxftype() == 'POLYLINE'


def test_closed_arrow_doc_r2000():
    doc = ezdxf.new2(dxfversion='R2000', setup=True)
    blocks = doc.blocks
    name = ARROWS.create_block(blocks, ARROWS.closed)
    arrow_entities = list(blocks.get(name))
    assert arrow_entities[0].dxftype() == 'LWPOLYLINE'


