# Copyright (C) 2019, Manfred Moitzi
# License: MIT License
# Created: 2019-02-24
import pytest
import ezdxf


@pytest.fixture(scope='module')
def msp():
    doc = ezdxf.new()
    return doc.modelspace()


def test_create_blockref(msp):
    blockref = msp.add_blockref("TESTBLOCK", (0, 0))
    assert blockref.dxf.name == 'TESTBLOCK'
    assert blockref.dxf.insert == (0., 0.)


def test_blockref_attrib_get_flags(msp):
    blockref = msp.add_blockref("TESTBLOCK", (0, 0))
    attrib = blockref.add_attrib('TAG1', "Text1", (0, 1))
    assert attrib.is_const is False
    assert attrib.is_invisible is False
    assert attrib.is_verify is False
    assert attrib.is_preset is False


def test_blockref_attrib_set_flags(msp):
    blockref = msp.add_blockref("TESTBLOCK", (0, 0))
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


def test_blockref_add_new_attribs(msp):
    entity_count = len(msp)
    db_count = len(msp.entitydb)
    blockref = msp.add_blockref("TESTBLOCK", (0, 0))
    blockref.add_attrib('TEST', 'text', (0, 0))
    assert len(msp) == entity_count+1
    assert len(msp.entitydb) == db_count+3  # insert + attrib + seqend

    assert blockref.attribs_follow == 1
    attrib = blockref.get_attrib('TEST')
    assert attrib.dxf.text == 'text'


def test_blockref_add_to_attribs(msp):
    blockref = msp.add_blockref("TESTBLOCK", (0, 0))
    blockref.add_attrib('TEST1', 'text1', (0, 0))
    blockref.add_attrib('TEST2', 'text2', (0, 0))
    assert ['TEST1', 'TEST2'] == [attrib.dxf.tag for attrib in blockref.attribs]


def test_blockref_place(msp):
    blockref = msp.add_blockref("TESTBLOCK", (0, 0))
    blockref.place(insert=(1, 2), scale=(0.5, 0.4, 0.3), rotation=37.0)
    assert blockref.dxf.insert == (1, 2)
    assert blockref.dxf.xscale == .5
    assert blockref.dxf.yscale == .4
    assert blockref.dxf.zscale == .3
    assert blockref.dxf.rotation == 37


def test_lockref_grid(msp):
    blockref = msp.add_blockref("TESTBLOCK", (0, 0))
    blockref.grid(size=(2, 3), spacing=(5, 10))
    assert blockref.dxf.row_count == 2
    assert blockref.dxf.column_count == 3
    assert blockref.dxf.row_spacing == 5
    assert blockref.dxf.column_spacing == 10


def test_blockref_attribs_follow_abuse(msp):
    blockref = msp.add_blockref("TESTBLOCK", (0, 0))
    assert len(blockref.attribs) == 0, 'Attrib count should be 0'
    assert blockref.has_attrib('TEST') is False, 'Attrib should not exists'

    blockref.add_attrib('TEST', 'Text')
    assert len(blockref.attribs) == 1
    assert blockref.attribs_follow is True


def test_blockref_delete_not_existing_attrib(msp):
    blockref = msp.add_blockref("TESTBLOCK", (0, 0))
    with pytest.raises(KeyError):
        blockref.delete_attrib('TEST')


def test_blockref_delete_not_existing_attrib_without_exception(msp):
    blockref = msp.add_blockref("TESTBLOCK", (0, 0))
    # ignore=True, should ignore not existing ATTRIBS
    blockref.delete_attrib('TEST', ignore=True)
    assert True


def test_blockref_delete_last_attrib(msp):
    blockref = msp.add_blockref("TESTBLOCK", (0, 0))
    blockref.add_attrib('TEST', 'Text')
    assert blockref.has_attrib('TEST') is True

    # delete last attrib
    blockref.delete_attrib('TEST')
    assert len(blockref.attribs) == 0
    assert blockref.dxf.attribs_follow == 0


def test_blockref_delete_one_of_many_attribs(msp):
    blockref = msp.add_blockref("TESTBLOCK", (0, 0))
    blockref.add_attrib('TEST0', 'Text')
    blockref.add_attrib('TEST1', 'Text')
    blockref.add_attrib('TEST2', 'Text')
    assert len(blockref.attribs) == 3
    assert blockref.attribs_follow is True

    blockref.delete_attrib('TEST1')
    assert len(blockref.attribs) == 2
    assert blockref.attribs_follow is True

    assert blockref.has_attrib('TEST0') is True
    assert blockref.has_attrib('TEST1') is False
    assert blockref.has_attrib('TEST2') is True


def test_blockref_delete_first_of_many_attribs(msp):
    blockref = msp.add_blockref("TESTBLOCK", (0, 0))
    blockref.add_attrib('TEST0', 'Text')
    blockref.add_attrib('TEST1', 'Text')
    assert len(blockref.attribs) == 2
    assert blockref.attribs_follow is True

    blockref.delete_attrib('TEST0')
    assert len(blockref.attribs) == 1
    assert blockref.attribs_follow is True

    assert blockref.has_attrib('TEST0') is False
    assert blockref.has_attrib('TEST1') is True


def test_blockref_delete_all_attribs(msp):
    blockref = msp.add_blockref("TESTBLOCK", (0, 0))
    # deleting none existing attribs, is ok
    blockref.delete_all_attribs()
    assert len(blockref.attribs) == 0
    assert blockref.dxf.attribs_follow == 0

    blockref.add_attrib('TEST0', 'Text')
    blockref.add_attrib('TEST1', 'Text')
    blockref.add_attrib('TEST2', 'Text')
    assert len(blockref.attribs) == 3
    assert blockref.attribs_follow is True

    blockref.delete_all_attribs()
    assert len(blockref.attribs) == 0
    assert blockref.dxf.attribs_follow == 0
