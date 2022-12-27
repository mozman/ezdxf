# Copyright (c) 2011-2022, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.sections.tables import TablesSection
from ezdxf.lldxf.tagwriter import TagCollector


@pytest.fixture(scope="module")
def tables():
    doc = ezdxf.new()
    return doc.tables


def test_constructor(tables):
    assert tables.layers is not None
    assert tables.linetypes is not None
    assert tables.appids is not None
    assert tables.styles is not None
    assert tables.dimstyles is not None
    assert tables.views is not None
    assert tables.viewports is not None
    assert tables.ucs is not None
    assert tables.block_records is not None


def test_getattr_upper_case(tables):
    with pytest.raises(AttributeError):
        _ = tables.LINETYPES


def test_error_getattr(tables):
    with pytest.raises(AttributeError):
        _ = tables.test


class TestAddLayerTableEntry:
    def test_add_layer(self, tables: TablesSection):
        layer = tables.layers.add(
            "NEW_LAYER",
            color=2,
            true_color=ezdxf.rgb2int((0x10, 0x20, 0x30)),
            linetype="DASHED",
            lineweight=18,
            plot=True,
        )
        assert layer.dxf.name == "NEW_LAYER"
        assert layer.dxf.color == 2
        assert layer.dxf.true_color == 0x00102030
        assert layer.dxf.linetype == "DASHED", "no check if line type exist!"
        assert layer.dxf.lineweight == 18
        assert layer.dxf.plot == 1

    def test_check_invalid_aci_color(self, tables: TablesSection):
        with pytest.raises(ValueError):
            tables.layers.add("INVALID_ACI", color=300)

    def test_check_invalid_line_weight(self, tables: TablesSection):
        with pytest.raises(ValueError):
            tables.layers.add("INVALID_LINE_WEIGHT", lineweight=300)


class TestTextStyleTable:
    def test_add_new_ttf_font_text_style(self, tables: TablesSection):
        style = tables.styles.add(
            "NEW_STYLE", font="Arial.ttf", dxfattribs={"flags": 3}
        )
        assert style.dxf.name == "NEW_STYLE"
        assert style.dxf.font == "Arial.ttf"
        assert style.dxf.flags == 3

    def test_add_new_shape_file(self, tables: TablesSection):
        style = tables.styles.add_shx("shapes1.shx")
        assert style.dxf.name == "", "shape files have no name"
        assert style.dxf.font == "shapes1.shx"
        assert style.dxf.flags == 1

        # can not add same shape file twice:
        with pytest.raises(ezdxf.const.DXFTableEntryError):
            tables.styles.add_shx("shapes1.shx")

    def test_add_multiple_shape_files(self, tables: TablesSection):
        style1 = tables.styles.add_shx("shapes4.shx")
        style2 = tables.styles.add_shx("shapes5.shx")
        assert tables.styles.find_shx(style1.dxf.font) is not None
        assert tables.styles.find_shx(style2.dxf.font) is not None

    def test_get_shape_file(self, tables: TablesSection):
        style = tables.styles.get_shx("shapes2.shx")
        assert style.dxf.name == "", "shape files have no name"
        assert style.dxf.font == "shapes2.shx"
        assert style.dxf.flags == 1

        style2 = tables.styles.get_shx("shapes2.shx")
        assert style is style2

    def test_find_shape_file(self, tables: TablesSection):
        tables.styles.add_shx("shapes3.shx")
        style = tables.styles.find_shx("shapes3.shx")
        assert style.dxf.font == "shapes3.shx"

    def test_if_shape_file_entry_exist(self, tables: TablesSection):
        assert tables.styles.find_shx("unknown.shx") is None

    def test_discard_shape_files(self, tables: TablesSection):
        style1 = tables.styles.add_shx("shapes6.shx")
        style2 = tables.styles.add_shx("shapes7.shx")
        tables.styles.discard_shx("shapes6.shx")
        tables.styles.discard_shx("shapes7.shx")
        assert tables.styles.find_shx(style1.dxf.font) is None
        assert tables.styles.find_shx(style2.dxf.font) is None

    def test_discard_not_existing_shape_file(self, tables: TablesSection):
        assert tables.styles.find_shx("shapes8.shx") is None
        tables.styles.discard_shx("shapes8.shx")  # should not raise an exception

    def test_export_multiple_shape_file_entries(self, tables: TablesSection):
        doc = ezdxf.new()
        doc.styles.add_shx("export1.shx")
        doc.styles.add_shx("export2.shx")

        tagwriter = TagCollector()
        doc.styles.export_dxf(tagwriter)
        font_names = [tag.value for tag in tagwriter.tags if tag.code == 3]
        assert len(font_names) == 3
        assert "export1.shx" in font_names
        assert "export2.shx" in font_names
        assert "txt" in font_names, "expected font of default text style STANDARD"


def test_add_new_line_type(tables: TablesSection):
    ltype = tables.linetypes.add(
        "SIMPLE_LINE_TYPE", [0.2, 0.1, -0.1], description="description"
    )
    assert ltype.dxf.name == "SIMPLE_LINE_TYPE"
    assert ltype.dxf.description == "description"
    # Correct pattern creation is tested in test suite 121.
