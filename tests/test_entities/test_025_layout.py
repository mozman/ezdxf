# Created: 25.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new2()


@pytest.fixture(scope='module')
def modelspace(doc):
    return doc.modelspace()


@pytest.fixture(scope='module')
def paperspace(doc):
    return doc.layout()


def test_dxffactory_property(doc, modelspace):
    line = modelspace.add_line((0, 0), (1, 1))
    assert doc.dxffactory is line.dxffactory


def test_delete_entity():
    doc = ezdxf.new('AC1009')
    layout = doc.modelspace()
    for _ in range(5):
        layout.add_line((0, 0), (10, 0))
    lines = layout.query('LINE')
    assert 5 == len(lines)
    line3 = lines[2]
    layout.delete_entity(line3)
    assert line3.dxf.paperspace < 0, "Paper space attribute has to be invalid (<0)."
    assert line3 not in layout
    assert line3.dxf.handle not in doc.entitydb


def test_delete_all_entities(doc):
    paperspace = doc.layout()
    paperspace_count = len(paperspace)
    modelspace = doc.modelspace()
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


def test_iter_layout(doc):
    paperspace = doc.layout()
    paperspace.delete_all_entities()
    paperspace.add_line((0, 0), (1, 1))
    paperspace.add_line((0, 0), (1, 1))
    entities = list(paperspace)
    assert len(entities) == 2
    assert entities[0].is_alive is True


def test_query_entities(doc):
    paperspace = doc.layout()
    paperspace.add_line((0, 0), (1, 1), dxfattribs={'layer': 'lay_lines'})
    paperspace.add_line((0, 0), (1, 1), dxfattribs={'layer': 'lay_lines'})
    entities = paperspace.query('*[layer ? "lay_.*"]')
    assert len(entities) == 2
    assert entities[0].doc is doc


def test_model_space_get_layout_for_entity(doc, modelspace):
    line = modelspace.add_line((0, 0), (1, 1))
    layout = doc.layouts.get_layout_for_entity(line)
    assert modelspace is layout


def test_paper_space_get_layout_for_entity(doc):
    paperspace = doc.layout()
    line = paperspace.add_line((0, 0), (1, 1))
    layout = doc.layouts.get_layout_for_entity(line)
    assert paperspace is layout


def test_default_entity_settings(modelspace):
    line = modelspace.add_line((0, 0), (1, 1))
    assert '0' == line.dxf.layer
    assert 256 == line.dxf.color
    assert 'BYLAYER' == line.dxf.linetype
    assert (0.0, 0.0, 1.0) == line.dxf.extrusion


def test_clone_dxfattribs(modelspace):
    line = modelspace.add_line((0, 0), (1, 1))
    attribs = line.dxfattribs()
    assert 'extrusion' not in attribs, "Don't clone unset attribs with default values."


def test_invalid_layer_name(modelspace):
    with pytest.raises(ezdxf.DXFInvalidLayerName):
        modelspace.add_line((0, 0), (1, 1), dxfattribs={'layer': 'InvalidName*'})
