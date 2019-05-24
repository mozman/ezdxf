# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
import pytest
import ezdxf


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new()


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


def test_direct_interface(entity):
    xdict = entity.get_extension_dict()
    placeholder = xdict.add_placeholder('TEST')
    assert 'TEST' in xdict
    placeholder2 = xdict['TEST']
    assert placeholder is placeholder2
    xdict['TEST2'] = placeholder2


def test_copy_entity(doc, entity):
    xdict = entity.get_extension_dict()  # create a new extension dict if not exists
    xdict.add_placeholder('Test')

    new_entity = entity.copy()
    # copying of extension dict is not supported
    assert new_entity.has_extension_dict() is False


def test_line_new_extension_dict(doc):
    msp = doc.modelspace()
    entity = msp.add_line((0, 0), (10, 0))
    assert entity.has_extension_dict() is False
    xdict = entity.get_extension_dict()
    dxf_dict = xdict.dictionary
    assert dxf_dict.dxftype() == 'DICTIONARY'
    assert dxf_dict.dxf.owner == entity.dxf.handle
    assert entity.has_app_data('{ACAD_XDICTIONARY') is False, 'extension dictionary is a separated storage'
    assert entity.has_extension_dict() is True

    xdict2 = entity.get_extension_dict()
    dxf_dict2 = xdict2.dictionary
    assert dxf_dict.dxf.handle == dxf_dict2.dxf.handle


def test_del_entity_with_ext_dict(doc):
    msp = doc.modelspace()
    entity = msp.add_line((0, 0), (10, 0))
    xdict = entity.get_extension_dict()

    objects = doc.objects
    assert xdict.dictionary in objects
    store_xdict = xdict.dictionary
    msp.delete_entity(entity)
    assert xdict.is_alive is False
    assert store_xdict not in objects
