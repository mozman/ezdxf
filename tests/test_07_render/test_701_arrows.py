# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf.render.arrows import ARROWS
from ezdxf.layouts import VirtualLayout


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
    doc = ezdxf.new(dxfversion='R12', setup=True)
    blocks = doc.blocks
    name = ARROWS.create_block(blocks, ARROWS.closed)
    arrow_entities = list(blocks.get(name))
    assert arrow_entities[0].dxftype() == 'POLYLINE'


def test_closed_arrow_doc_r2000():
    doc = ezdxf.new(dxfversion='R2000', setup=True)
    blocks = doc.blocks
    name = ARROWS.create_block(blocks, ARROWS.closed)
    arrow_entities = list(blocks.get(name))
    assert arrow_entities[0].dxftype() == 'LWPOLYLINE'


def test_render_arrow():
    layout = VirtualLayout()
    ARROWS.render_arrow(layout, ARROWS.closed, insert=(0, 0, 0))
    assert len(layout) > 0


def test_virtual_entities():
    entities = list(ARROWS.virtual_entities(ARROWS.closed, insert=(0, 0, 0)))
    assert len(entities) > 0
