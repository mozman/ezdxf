# Copyright (c) 2011-2024, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.lldxf import const
from ezdxf.entities import MText, Insert


@pytest.fixture
def doc():
    return ezdxf.new()


@pytest.fixture
def block(doc):
    block = doc.blocks.new("TEST")
    block.add_attdef("TAG1", (0, 0), text="default text1")
    block.add_attdef("TAG2", (0, 5), text="default text2")
    return block


def test_auto_blockref(doc, block):
    values = {"TAG1": "text1", "TAG2": "text2"}
    msp = doc.modelspace()
    blockref = msp.add_auto_blockref("TEST", (0, 0), values)
    autoblock = doc.blocks[blockref.dxf.name]
    entities = list(autoblock)
    insert = entities[0]
    assert isinstance(insert, Insert) is True

    attrib1, attrib2 = insert.attribs
    assert attrib1.dxftype() == "ATTRIB"
    assert attrib1.dxf.tag == "TAG1"
    assert attrib1.dxf.text == "text1"
    assert attrib1.dxf.attribute_type == const.ATTRIB_TYPE_SINGLE_LINE

    assert attrib2.dxftype() == "ATTRIB"
    assert attrib2.dxf.tag == "TAG2"
    assert attrib2.dxf.text == "text2"
    assert attrib2.dxf.attribute_type == const.ATTRIB_TYPE_SINGLE_LINE


def test_add_auto_attribs(doc, block):
    values = {"TAG1": "text1", "TAG2": "text2"}
    msp = doc.modelspace()
    blockref = msp.add_blockref("TEST", (0, 0)).add_auto_attribs(values)
    assert blockref.dxftype() == "INSERT"

    attrib1, attrib2 = blockref.attribs
    assert attrib1.dxftype() == "ATTRIB"
    assert attrib1.dxf.tag == "TAG1"
    assert attrib1.dxf.text == "text1"
    assert attrib1.dxf.attribute_type == const.ATTRIB_TYPE_SINGLE_LINE

    assert attrib2.dxftype() == "ATTRIB"
    assert attrib2.dxf.tag == "TAG2"
    assert attrib2.dxf.text == "text2"
    assert attrib2.dxf.attribute_type == const.ATTRIB_TYPE_SINGLE_LINE


def test_add_auto_attribs_with_default_text(doc, block):
    msp = doc.modelspace()
    blockref = msp.add_blockref("TEST", (0, 0)).add_auto_attribs({})
    attrib1, attrib2 = blockref.attribs
    assert attrib1.dxf.text == "default text1"
    assert attrib2.dxf.text == "default text2"


def test_add_auto_attribs_with_missing_tag():
    doc = ezdxf.new()
    msp = doc.modelspace()
    blocks = doc.blocks.new("TEST")
    attdef = blocks.add_attdef("TAG1", (0, 0))
    attdef.dxf.discard("tag")  # simulate erroneous DXF input

    blockref = msp.add_blockref("TEST", (0, 0)).add_auto_attribs({"TAG1": "Test"})
    assert blockref.has_attrib("TAG1") is False


def test_add_auto_attribs_with_missing_location():
    doc = ezdxf.new()
    msp = doc.modelspace()
    blocks = doc.blocks.new("TEST")
    attdef = blocks.add_attdef("TAG1", (0, 0))
    attdef.dxf.discard("insert")  # simulate erroneous DXF input

    blockref = msp.add_blockref("TEST", (0, 0)).add_auto_attribs({"TAG1": "Test"})
    assert blockref.has_attrib("TAG1") is False


def test_has_attdef(block):
    assert block.has_attdef("TAG1") is True
    assert block.has_attdef("TAG_Z") is False


def test_get_attdef(block):
    attdef = block.get_attdef("TAG1")
    assert attdef.dxf.tag == "TAG1"
    assert block.get_attdef("TAG1_Z") is None


def test_get_attdef_text(block):
    block.add_attdef("TAGX", insert=(0, 0), text="PRESET_TEXT")
    text = block.get_attdef_text("TAGX")
    assert text == "PRESET_TEXT"


def test_attdef_getter_properties(block):
    attrib = block.get_attdef("TAG1")

    assert attrib.is_const is False
    assert attrib.is_invisible is False
    assert attrib.is_verify is False
    assert attrib.is_preset is False


def test_attdef_setter_properties(block):
    attrib = block.get_attdef("TAG1")

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


class TestMultiLineAttribs:
    @pytest.fixture
    def doc(self):
        return ezdxf.new()

    @pytest.fixture
    def block(self, doc):
        block = doc.blocks.new("TEST")
        attdef = block.add_attdef("TAG1")
        # Note: \n is converted to \P automatically at DXF export
        mtext = MText.new(dxfattribs={"insert": (1, 1), "text": "default\ntext"})
        attdef.embed_mtext(mtext)
        return block

    def test_has_multi_line_attdef(self, block):
        attdef = block.get_attdef("TAG1")
        assert attdef is not None
        assert attdef.has_embedded_mtext_entity is True
        assert attdef.dxf.attribute_type == const.ATTDEF_TYPE_MULTI_LINE

    def test_multi_line_attdef_properties(self, block):
        attdef = block.get_attdef("TAG1")
        assert attdef is not None
        assert attdef.dxf.insert == (1, 1)
        assert attdef.dxf.text == "default", "expected just first line"

        mtext = attdef.virtual_mtext_entity()
        assert isinstance(mtext, MText) is True

        assert mtext.dxf.insert == (1, 1)
        assert mtext.dxf.text == "default\ntext", "expected all lines"

    def test_add_auto_multi_line_attrib(self, doc, block):
        msp = doc.modelspace()
        insert = msp.add_blockref(block.name, insert=(2, 3))
        assert insert is not None

        insert.add_auto_attribs({"TAG1": "MultiLine\nAttribute"})

        attrib = insert.attribs[0]
        assert attrib is not None

        assert attrib.dxf.insert == (3, 4)
        assert attrib.dxf.text == "MultiLine", "expected just first line"
        assert attrib.has_embedded_mtext_entity is True
        assert attrib.dxf.attribute_type == const.ATTRIB_TYPE_MULTI_LINE

        mtext = attrib.virtual_mtext_entity()
        assert isinstance(mtext, MText) is True

        assert mtext.dxf.insert == (3, 4)
        assert mtext.dxf.text == "MultiLine\nAttribute", "expected all lines"
