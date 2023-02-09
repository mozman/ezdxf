# Created: 25.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope="module")
def doc():
    return ezdxf.new()


@pytest.fixture(scope="module")
def modelspace(doc):
    return doc.modelspace()


@pytest.fixture(scope="module")
def paperspace(doc):
    return doc.layout()


def test_default_properties(modelspace):
    assert modelspace.units == 0


def test_set_units(modelspace):
    assert modelspace.units == 0
    modelspace.units = 6
    assert modelspace.units == 6
    # reset - because module scope
    modelspace.units = 0


def test_delete_entity():
    doc = ezdxf.new("R12")
    layout = doc.modelspace()
    for _ in range(5):
        layout.add_line((0, 0), (10, 0))
    lines = layout.query("LINE")
    assert 5 == len(lines)
    line3 = lines[2]
    layout.delete_entity(line3)
    assert line3.is_alive is False


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
    paperspace.add_line((0, 0), (1, 1), dxfattribs={"layer": "lay_lines"})
    paperspace.add_line((0, 0), (1, 1), dxfattribs={"layer": "lay_lines"})
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
    assert "0" == line.dxf.layer
    assert 256 == line.dxf.color
    assert "BYLAYER" == line.dxf.linetype
    assert (0.0, 0.0, 1.0) == line.dxf.extrusion


def test_clone_dxfattribs(modelspace):
    line = modelspace.add_line((0, 0), (1, 1))
    attribs = line.dxfattribs()
    assert (
        "extrusion" not in attribs
    ), "Don't clone unset attribs with default values."


def test_invalid_layer_name(modelspace):
    with pytest.raises(ezdxf.DXFValueError):
        modelspace.add_line(
            (0, 0), (1, 1), dxfattribs={"layer": "InvalidName*"}
        )


def test_create_layout(doc):
    assert (
        len(doc.layouts) == 2
    ), "New drawing should have 1 model space and 1 paper space"

    # create a new layout
    layout = doc.layouts.new("ezdxf")
    assert "ezdxf" in doc.layouts
    assert len(layout) == 0, "New layout should contain no entities"

    with pytest.raises(ezdxf.DXFValueError):
        doc.layouts.new('invalid characters: <>/":;?*|=`')

    layout.page_setup()  # default paper setup
    assert len(layout) == 1, "missing 'main' viewport entity"


class TestAcquireLayouts:
    @pytest.fixture(scope="class")
    def doc(self):
        doc = ezdxf.new()
        doc.layouts.new("Layout2")
        doc.layouts.new("Layout3")
        doc.layouts.set_active_layout("Layout3")
        return doc

    def test_get_modelspace(self, doc):
        msp = doc.modelspace()
        assert msp.name == "Model"

    def test_layout_returns_first_layout_in_tab_order(self, doc):
        psp = doc.layout()
        assert psp.name == "Layout1"
        assert psp.is_active_paperspace is False

    def test_paperspace_returns_active_paperspace_by_default(self, doc):
        psp = doc.paperspace()
        assert psp.name == "Layout3"
        assert psp.is_active_paperspace is True

    def test_paperspace_returns_paperspace_by_name(self, doc):
        psp = doc.paperspace("Layout2")
        assert psp.name == "Layout2"
        assert psp.is_active_paperspace is False

    def test_paperspace_raises_key_error_if_not_exists(self, doc):
        with pytest.raises(KeyError):
            doc.paperspace("DoesNotExist")

    def test_paperspace_raises_key_error_for_modelspace(self, doc):
        with pytest.raises(KeyError):
            doc.paperspace("Model")
