# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture
def src():
    doc = ezdxf.new()
    doc.layers.new('EXTRA_LAYER')
    doc.linetypes.new('EXTRA_LT')
    doc.styles.new('EXTRA_STYLE')
    attribs = {
        'linetype': 'EXTRA_LT',
        'layer': 'EXTRA_LAYER',
    }
    msp = doc.modelspace()

    msp.add_line((0, 0), (1, 0), dxfattribs=attribs)
    msp.add_text('Text', dxfattribs={
        'layer': 'EXTRA_LAYER',
        'style': 'EXTRA_STYLE',
    })
    msp.add_polyline2d([(0, 0), (1, 1), (2, 2)], dxfattribs=attribs)
    return msp


@pytest.fixture
def target():
    doc = ezdxf.new()
    # for different handles
    for x in range(10):
        doc.entitydb.next_handle()
    return doc.modelspace()


def test_01_copy_foreign_entities_reset_resources(src, target):
    src_length = len(src)
    line = src[0]
    assert line.dxftype() == 'LINE'
    target.add_foreign_entity(line, copy=True)
    line_copy = target[0]
    assert line_copy.dxftype() == 'LINE'
    # check if copied not moved
    assert len(src) == src_length
    assert len(target) == 1
    assert line_copy.doc is not None
    assert line_copy.doc is not line.doc
    assert line_copy.dxf.handle != line.dxf.handle
    # check resources
    # layer is preserved
    assert line_copy.dxf.layer == line.dxf.layer
    assert line_copy.dxf.linetype == 'BYLAYER'


def test_02_copy_foreign_entities_with_resources(src, target):
    line = src[0]
    assert line.dxftype() == 'LINE'
    assert line.dxf.layer != '0'
    # create source layer
    target.doc.layers.new(line.dxf.layer)
    target.doc.linetypes.new(line.dxf.linetype)
    target.add_foreign_entity(line, copy=True)
    line_copy = target[0]
    assert line_copy.dxftype() == 'LINE'
    # check resources
    assert line_copy.dxf.layer == line.dxf.layer
    assert line_copy.dxf.linetype == line.dxf.linetype


def test_03_move_foreign_entities(src, target):
    src_length = len(src)
    text = src[1]
    assert text.dxftype() == 'TEXT'
    target.add_foreign_entity(text, copy=False)
    text_moved = target[0]
    assert text_moved.dxftype() == 'TEXT'

    # check if moved not copied
    assert len(src) == src_length - 1
    assert len(target) == 1
    assert text_moved is text
    assert text_moved.doc is not None

    # check resources
    assert text_moved.dxf.layer == 'EXTRA_LAYER', 'layer should be preserved'
    assert text_moved.dxf.linetype == 'BYLAYER'
    assert text_moved.dxf.style == 'Standard'


def test_04_move_foreign_entities_with_resources(src, target):
    src_length = len(src)
    text = src[1]
    assert text.dxftype() == 'TEXT'
    layer = text.dxf.layer
    style = text.dxf.style
    target.doc.layers.new(layer)
    target.doc.styles.new(style)

    target.add_foreign_entity(text, copy=False)
    text_moved = target[0]
    assert text_moved.dxftype() == 'TEXT'

    # check if moved not copied
    assert len(src) == src_length - 1
    assert len(target) == 1
    assert text_moved is text
    assert text_moved.doc is not None

    # check resources
    assert text_moved.dxf.layer == layer
    assert text_moved.dxf.linetype == 'BYLAYER'
    assert text_moved.dxf.style == style


def test_05_copy_polyline_reset_resources(src, target):
    src_length = len(src)
    pline = src[2]
    assert pline.dxftype() == 'POLYLINE'
    target.add_foreign_entity(pline, copy=True)
    pline_copy = target[0]
    assert pline_copy.dxftype() == 'POLYLINE'
    # check if copied not moved
    assert len(src) == src_length
    assert len(target) == 1
    assert pline_copy.doc is not None
    assert pline_copy.doc is not pline.doc
    assert pline_copy.dxf.handle != pline.dxf.handle
    # check resources
    assert pline_copy.dxf.layer == 'EXTRA_LAYER', 'layer should be preserved'
    assert pline_copy.dxf.linetype == 'BYLAYER'
    # check vertices
    assert len(pline_copy.vertices) == len(pline.vertices)
    for v1, v2 in zip(pline_copy.vertices, pline.vertices):
        assert v1.dxf.handle != v2.dxf.handle
        assert v1.dxf.layer == 'EXTRA_LAYER', 'layer should be preserved'
        assert v1.dxf.linetype != v2.dxf.linetype


def test_06_move_polyline(src, target):
    src_length = len(src)
    pline = src[2]
    assert pline.dxftype() == 'POLYLINE'
    handles = [v.dxf.handle for v in pline.vertices]
    handles.append(pline.dxf.handle)

    target.add_foreign_entity(pline, copy=False)
    pline_move= target[0]
    assert pline_move.dxftype() == 'POLYLINE'
    # check if moved
    assert len(src) == src_length - 1
    assert len(target) == 1
    assert pline_move.doc is not None
    assert pline_move.doc is pline.doc

    # check removed entities
    for handle in handles:
        assert handle not in src.doc.entitydb


if __name__ == '__main__':
    pytest.main([__file__])
