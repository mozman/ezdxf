# Created: 25.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('AC1009')


@pytest.fixture(scope='module')
def modelspace(dwg):
    return dwg.modelspace()


@pytest.fixture(scope='module')
def paperspace(dwg):
    return dwg.layout()


def test_drawing_attribute(dwg, modelspace):
    line = modelspace.add_line((0, 0), (1, 1))
    assert dwg is line.drawing


def test_dxffactory_property(dwg, modelspace):
    line = modelspace.add_line((0, 0), (1, 1))
    assert dwg.dxffactory is line.dxffactory


def test_delete_entity():
    dwg = ezdxf.new('AC1009')
    layout = dwg.modelspace()
    for _ in range(5):
        layout.add_line((0, 0), (10, 0))
    lines = layout.query('LINE')
    assert 5 == len(lines)
    line3 = lines[2]
    layout.delete_entity(line3)
    assert line3.dxf.paperspace < 0, "Paper space attribute has to be invalid (<0)."
    assert line3 not in layout
    assert line3.dxf.handle not in dwg.entitydb


def test_delete_polyline(modelspace):
    entity_count = len(list(modelspace))
    pline = modelspace.add_polyline3d([(0, 0, 0), (1, 2, 3), (4, 5, 6)])
    assert entity_count+1 == len(list(modelspace)), "Expected 1x POLYLINE entity, VERTEX entities should be linked to the POLYLINE entity."
    modelspace.delete_entity(pline)
    assert entity_count == len(list(modelspace))


def test_delete_blockref_with_attribs(modelspace):
    entity_count = len(list(modelspace))
    blockref = modelspace.add_blockref("TESTBLOCK", (0, 0))
    blockref.add_attrib('TAG1', "Text1", (0, 1))
    blockref.add_attrib('TAG2', "Text2", (0, 2))
    blockref.add_attrib('TAG3', "Text3", (0, 3))
    assert entity_count+1 == len(list(modelspace)), "Expected 1x INSERT entity, ATTRIB entities should be linked to the INSERT entity."
    modelspace.delete_entity(blockref)
    assert entity_count == len(list(modelspace))


def test_delete_all_entities(dwg):
    paperspace = dwg.layout()
    paperspace_count = len(paperspace)
    modelspace = dwg.modelspace()
    modelspace_count = len(modelspace)
    for _ in range(5):
        modelspace.add_line((0, 0), (1, 1))
        paperspace.add_line((0, 0), (1, 1))

    assert modelspace_count + 5 == len(modelspace)
    assert paperspace_count + 5 == len(paperspace)

    modelspace.delete_all_entities()
    assert len(modelspace) == 0
    assert paperspace_count + 5 == len(paperspace)


def test_paper_space(paperspace):
    line = paperspace.add_line((0, 0), (1, 1))
    assert line.dxf.paperspace == 1


def test_iter_layout(dwg):
    paperspace = dwg.layout()
    paperspace.delete_all_entities()
    paperspace.add_line((0, 0), (1, 1))
    paperspace.add_line((0, 0), (1, 1))
    entities = list(paperspace)
    assert len(entities) == 2
    assert entities[0].drawing is dwg


def test_query_entities(dwg):
    paperspace = dwg.layout()
    paperspace.add_line((0, 0), (1, 1), dxfattribs={'layer': 'lay_lines'})
    paperspace.add_line((0, 0), (1, 1), dxfattribs={'layer': 'lay_lines'})
    entities = paperspace.query('*[layer ? "lay_.*"]')
    assert len(entities) == 2
    assert entities[0].drawing is dwg


def test_model_space_get_layout_for_entity(dwg, modelspace):
    line = modelspace.add_line((0, 0), (1, 1))
    layout = dwg.layouts.get_layout_for_entity(line)
    assert modelspace is layout


def test_paper_space_get_layout_for_entity(dwg):
    paperspace = dwg.layout()
    line = paperspace.add_line((0, 0), (1, 1))
    layout = dwg.layouts.get_layout_for_entity(line)
    assert paperspace is layout


def test_default_entity_settings(modelspace):
    line = modelspace.add_line((0, 0), (1, 1))
    assert '0' == line.dxf.layer
    assert 256 == line.dxf.color
    assert 'BYLAYER' == line.dxf.linetype
    assert (0.0, 0.0, 1.0) == line.dxf.extrusion


def test_clone_dxf_attribs(modelspace):
    line = modelspace.add_line((0, 0), (1, 1))
    attribs = line.clone_dxf_attribs()
    assert 'extrusion' not in attribs, "Don't clone unset attribs with default values."


def test_create_line(modelspace):
    line = modelspace.add_line((0, 0), (1, 1))
    assert line.dxf.start == (0., 0.)
    assert line.dxf.end == (1., 1.)


def test_create_point(modelspace):
    line = modelspace.add_point((1, 2))
    assert line.dxf.location == (1, 2)


def test_create_circle(modelspace):
    circle = modelspace.add_circle((3, 3), 5)
    assert circle.dxf.center == (3., 3.)
    assert circle.dxf.radius == 5.


def test_create_arc(modelspace):
    arc = modelspace.add_arc((3, 3), 5, 30, 60)
    assert arc.dxf.center == (3., 3.)
    assert arc.dxf.radius == 5.
    assert arc.dxf.start_angle == 30.
    assert arc.dxf.end_angle == 60.


def test_create_trace(modelspace):
    trace = modelspace.add_trace([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert trace[0] == (0, 0)
    assert trace.dxf.vtx1 == (1, 0)
    assert trace[2] == (1, 1)
    assert trace.dxf.vtx3 == (0, 1)


def test_create_solid(modelspace):
    trace = modelspace.add_solid([(0, 0), (1, 0), (1, 1)])
    assert trace.dxf.vtx0 == (0, 0)
    assert trace[1] == (1, 0)
    assert trace.dxf.vtx2 == (1, 1)
    assert trace[3] == (1, 1)


def test_create_3dface(modelspace):
    trace = modelspace.add_3dface([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)])
    assert trace.dxf.vtx0 == (0, 0, 0)
    assert trace[1] == (1, 0, 0)
    assert trace.dxf.vtx2 == (1, 1, 0)
    assert trace[3] == (0, 1, 0)


def test_create_text(modelspace):
    text = modelspace.add_text('text')
    assert text.dxf.text == 'text'


def test_text_set_alignment(modelspace):
    text = modelspace.add_text('text')
    text.set_pos((2, 2), align="TOP_CENTER")
    assert text.dxf.halign == 1
    assert text.dxf.valign == 3
    assert text.dxf.align_point == (2, 2)


def test_text_set_fit_alignment(modelspace):
    text = modelspace.add_text('text')
    text.set_pos((2, 2), (4, 2), align="FIT")
    assert text.dxf.halign == 5
    assert text.dxf.valign == 0
    assert text.dxf.insert == (2, 2)
    assert text.dxf.align_point == (4, 2)


def test_text_get_alignment(modelspace):
    text = modelspace.add_text('text')
    text.dxf.halign = 1
    text.dxf.valign = 3
    assert text.get_align() == 'TOP_CENTER'


def test_text_get_pos_TOP_CENTER(modelspace):
    text = modelspace.add_text('text')
    text.set_pos((2, 2), align="TOP_CENTER")
    align, p1, p2 = text.get_pos()
    assert align == "TOP_CENTER"
    assert p1 == (2, 2)
    assert p2 is None


def test_text_get_pos_LEFT(modelspace):
    text = modelspace.add_text('text')
    text.set_pos((2, 2))
    align, p1, p2 = text.get_pos()
    assert align == "LEFT"
    assert p1 == (2, 2)
    assert p2 is None


def test_create_shape(modelspace):
    shape = modelspace.add_shape("TestShape", (1, 2), 3.0)
    assert shape.dxf.name == "TestShape"
    assert shape.dxf.insert == (1.0, 2.0)
    assert shape.dxf.size == 3
    assert shape.dxf.rotation == 0
    assert shape.dxf.xscale == 1
    assert shape.dxf.oblique == 0

@pytest.fixture
def blockref(modelspace):
    return modelspace.add_blockref("TESTBLOCK", (0, 0))


def test_create_blockref(blockref):
    assert blockref.dxf.name == 'TESTBLOCK'
    assert blockref.dxf.insert == (0., 0.)


def test_blockref_attribs_getter_properties(blockref):
    attrib = blockref.add_attrib('TAG1', "Text1", (0, 1))

    assert attrib.is_const is False
    assert attrib.is_invisible is False
    assert attrib.is_verify is False
    assert attrib.is_preset is False


def test_blockref_attribs_setter_properties(blockref):
    attrib = blockref.add_attrib('TAG1', "Text1", (0, 1))

    assert attrib.is_const is False
    attrib.is_const = True
    assert attrib.is_const is True

    assert attrib.is_invisible is False
    attrib.is_invisible = True
    assert attrib.is_invisible is True

    assert attrib.is_verify is False
    attrib.is_verify = True
    assert attrib.is_verify is True

    assert attrib.is_preset is False
    attrib.is_preset = True
    assert attrib.is_preset is True


def test_blockref_add_new_attribs(blockref):
    blockref.add_attrib('TEST', 'text', (0, 0))
    assert blockref.dxf.attribs_follow == 1
    attrib = blockref.get_attrib('TEST')
    assert attrib.dxf.text == 'text'


def test_blockref_add_to_attribs(blockref):
    blockref.add_attrib('TEST1', 'text1', (0, 0))
    blockref.add_attrib('TEST2', 'text2', (0, 0))
    assert ['TEST1', 'TEST2'] == [attrib.dxf.tag for attrib in blockref.attribs()]


def test_blockref_has_seqend(modelspace, blockref):
    blockref.add_attrib('TEST1', 'text1', (0, 0))
    blockref.add_attrib('TEST2', 'text2', (0, 0))
    entity = blockref.get_attrib('TEST2')
    seqend = modelspace.entitydb[entity.tags.link]
    assert seqend.dxftype() == 'SEQEND'


def test_blockref_place(blockref):
    blockref.place(insert=(1, 2), scale=(0.5, 0.4, 0.3), rotation=37.0)
    assert blockref.dxf.insert == (1, 2)
    assert blockref.dxf.xscale == .5
    assert blockref.dxf.yscale == .4
    assert blockref.dxf.zscale == .3
    assert blockref.dxf.rotation == 37


def test_lockref_grid(blockref):
    blockref.grid(size=(2, 3), spacing=(5, 10))
    assert blockref.dxf.row_count == 2
    assert blockref.dxf.column_count == 3
    assert blockref.dxf.row_spacing == 5
    assert blockref.dxf.column_spacing == 10


def test_blockref_attribs_follow_abuse(blockref):
    # set attribs follow without attaching an ATTRIB entity
    blockref.dxf.attribs_follow = 1
    attribs = list(blockref.attribs())
    assert len(attribs) == 0, 'Attrib count should be 0'
    assert blockref.has_attrib('TEST') is False, 'Attrib should not exists'

    blockref.add_attrib('TEST', 'Text')
    assert len(list(blockref.attribs())) == 1


def test_blockref_delete_not_existing_attrib(blockref):
    with pytest.raises(KeyError):
        blockref.delete_attrib('TEST')


def test_blockref_delete_not_existing_attrib_no_exception(blockref):
    # ignore=True, should ignore not existing ATTRIBS
    blockref.delete_attrib('TEST', ignore=True)
    assert True


def test_blockref_delete_last_attrib(blockref):
    blockref.add_attrib('TEST', 'Text')
    assert blockref.has_attrib('TEST') is True

    # delete last attrib
    blockref.delete_attrib('TEST')
    assert len(list(blockref.attribs())) == 0
    assert blockref.dxf.attribs_follow == 0
    assert blockref.tags.link is None


def test_blockref_delete_one_of_many_attribs(blockref):
    blockref.add_attrib('TEST0', 'Text')
    blockref.add_attrib('TEST1', 'Text')
    blockref.add_attrib('TEST2', 'Text')
    assert len(list(blockref.attribs())) == 3
    assert blockref.dxf.attribs_follow == 1

    blockref.delete_attrib('TEST1')
    assert len(list(blockref.attribs())) == 2
    assert blockref.dxf.attribs_follow == 1

    assert blockref.has_attrib('TEST0') is True
    assert blockref.has_attrib('TEST1') is False
    assert blockref.has_attrib('TEST2') is True


def test_blockref_delete_first_of_many_attribs(blockref):
    blockref.add_attrib('TEST0', 'Text')
    blockref.add_attrib('TEST1', 'Text')
    assert len(list(blockref.attribs())) == 2
    assert blockref.dxf.attribs_follow == 1

    blockref.delete_attrib('TEST0')
    assert len(list(blockref.attribs())) == 1
    assert blockref.dxf.attribs_follow == 1

    assert blockref.has_attrib('TEST0') is False
    assert blockref.has_attrib('TEST1') is True


def test_blockref_delete_all_attribs(blockref):
    # deleting none existing attribs, is ok
    blockref.delete_all_attribs()
    assert len(list(blockref.attribs())) == 0
    assert blockref.dxf.attribs_follow == 0

    blockref.add_attrib('TEST0', 'Text')
    blockref.add_attrib('TEST1', 'Text')
    blockref.add_attrib('TEST2', 'Text')
    assert len(list(blockref.attribs())) == 3
    assert blockref.dxf.attribs_follow == 1

    blockref.delete_all_attribs()
    assert len(list(blockref.attribs())) == 0
    assert blockref.dxf.attribs_follow == 0
    assert blockref.tags.link is None


if __name__ == '__main__':
    pytest.main([__file__])
