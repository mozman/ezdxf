# Created: 03.04.2011
# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


class TestAutoBlockReference:
    @pytest.fixture
    def doc(self):
        return ezdxf.new2()

    @pytest.fixture
    def block(self, doc):
        block = doc.blocks.new('TEST')
        block.add_attdef('TAG1', (0, 0))
        block.add_attdef('TAG2', (0, 5))
        return block

    def test_create_auto_attribs(self, doc, block):
        values = {'TAG1': 'text1', 'TAG2': 'text2'}
        msp = doc.modelspace()
        blockref = msp.add_auto_blockref('TEST', (0, 0), values)
        autoblock = doc.blocks[blockref.dxf.name]
        entities = list(autoblock)
        insert = entities[0]
        assert insert.dxftype() == 'INSERT'

        attrib1, attrib2 = insert.attribs
        assert attrib1.dxftype() == 'ATTRIB'
        assert attrib1.dxf.tag == 'TAG1'
        assert attrib1.dxf.text == 'text1'
        assert attrib2.dxftype() == 'ATTRIB'
        assert attrib2.dxf.tag == 'TAG2'
        assert attrib2.dxf.text == 'text2'

    def test_has_attdef(self, block):
        assert block.has_attdef('TAG1') is True
        assert block.has_attdef('TAG_Z') is False

    def test_get_attdef(self, block):
        attdef = block.get_attdef('TAG1')
        assert attdef.dxf.tag == 'TAG1'
        assert block.get_attdef('TAG1_Z') is None

    def test_get_attdef_text(self, block):
        block.add_attdef('TAGX', (0, 0), text='PRESET_TEXT')
        text = block.get_attdef_text('TAGX')
        assert text == 'PRESET_TEXT'

    def test_attdef_getter_properties(self, block):
        attrib = block.get_attdef('TAG1')

        assert attrib.is_const is False
        assert attrib.is_invisible is False
        assert attrib.is_verify is False
        assert attrib.is_preset is False

    def test_attdef_setter_properties(self, block):
        attrib = block.get_attdef('TAG1')

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
