# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
import pytest
import ezdxf


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new2()


@pytest.fixture()
def entity(doc):
    msp = doc.modelspace()
    return msp.add_line((0, 0), (1, 1))


def test_new_extension_dict(doc, entity):
    assert entity.has_extension_dict() is False
    xdict = entity.get_extension_dict()
    assert xdict.dictionary.dxftype() == 'DICTIONARY'
    assert len(xdict.dictionary) == 0
    placeholder = xdict.add_placeholder('TEST')
    assert len(xdict.dictionary) == 1
    assert placeholder.dxf.owner == xdict.dictionary.dxf.handle
    assert 'TEST' in xdict.dictionary


def test_copy_entity(doc, entity):
    xdict = entity.get_extension_dict()  # create a new extension dict if not exists
    placeholder = xdict.add_placeholder('Test')

    new_entity = entity.copy()
    assert new_entity.has_extension_dict()
    assert entity.extension_dict is not new_entity.extension_dict
    assert entity.dxf.handle == entity.extension_dict.dictionary.dxf.owner, 'owner handle should be entity handle'

    new_placeholder = new_entity.extension_dict.dictionary['Test']
    assert new_placeholder.dxf.owner != placeholder.dxf.owner
    assert new_entity.extension_dict.dictionary['Test'].dxf.owner != placeholder.dxf.owner

    new_entity.extension_dict.add_placeholder('Test2')
    assert len(entity.extension_dict.dictionary) == 1
    assert len(new_entity.extension_dict.dictionary) == 2

