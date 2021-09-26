# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
import pytest
import ezdxf
from ezdxf.entities import factory, DXFEntity
from ezdxf.entities.xdict import ExtensionDict


@pytest.fixture(scope="module")
def doc():
    return ezdxf.new()


@pytest.fixture()
def entity(doc):
    msp = doc.modelspace()
    return msp.add_line((0, 0), (1, 1))


def test_new_extension_dict(doc, entity):
    factory.bind(entity, doc)
    assert entity.has_extension_dict is False
    xdict = entity.new_extension_dict()
    assert xdict.dictionary.dxftype() == "DICTIONARY"
    assert len(xdict.dictionary) == 0

    placeholder = xdict.add_placeholder("TEST")
    assert len(xdict.dictionary) == 1
    assert placeholder.dxf.owner == xdict.dictionary.dxf.handle
    assert "TEST" in xdict.dictionary


def test_direct_interface(doc, entity):
    factory.bind(entity, doc)
    xdict = entity.new_extension_dict()
    placeholder = xdict.add_placeholder("TEST")
    assert "TEST" in xdict
    placeholder2 = xdict["TEST"]
    assert placeholder is placeholder2
    xdict["TEST2"] = placeholder2


def test_get_returns_none_for_non_existing_entries(doc):
    xdict = ExtensionDict(doc.objects.add_dictionary())
    assert xdict.get("ABC") is None


def test_supports_handle_property(doc):
    xdict = ExtensionDict.new("ABBA", doc)
    assert isinstance(xdict.handle, str)


def test_line_new_extension_dict(doc):
    msp = doc.modelspace()
    entity = msp.add_line((0, 0), (10, 0))
    assert entity.has_extension_dict is False
    xdict = entity.new_extension_dict()
    dxf_dict = xdict.dictionary
    assert dxf_dict.dxftype() == "DICTIONARY"
    assert dxf_dict.dxf.owner == entity.dxf.handle
    assert (
        entity.has_app_data("{ACAD_XDICTIONARY") is False
    ), "extension dictionary is a separated storage"
    assert entity.has_extension_dict is True

    xdict2 = entity.get_extension_dict()
    dxf_dict2 = xdict2.dictionary
    assert dxf_dict.dxf.handle == dxf_dict2.dxf.handle


def test_del_entity_with_ext_dict(doc):
    msp = doc.modelspace()
    entity = msp.add_line((0, 0), (10, 0))
    xdict = entity.new_extension_dict()

    objects = doc.objects
    assert xdict.dictionary in objects
    store_xdict = xdict.dictionary
    msp.delete_entity(entity)
    doc.objects.purge()
    assert xdict.is_alive is False
    assert store_xdict not in objects


def test_discard_existing_extension_dict(doc):
    msp = doc.modelspace()
    entity = msp.add_line((0, 0), (10, 0))
    xdict = entity.new_extension_dict()
    dictionary = xdict.dictionary
    placeholder = xdict.add_placeholder("TEST")
    entity.discard_extension_dict()
    assert placeholder.is_alive is False
    assert dictionary.is_alive is False
    assert xdict.is_alive is False
    assert entity.has_extension_dict is False


def test_discard_non_existing_extension_dict_without_exception(doc):
    msp = doc.modelspace()
    entity = msp.add_line((0, 0), (10, 0))
    entity.discard_extension_dict()
    assert entity.has_extension_dict is False


def test_multiple_destroy_calls(doc, entity):
    xdict = ExtensionDict.new("ABBA", doc)
    xdict.destroy()
    xdict.destroy(), "2nd call should not raise an exception"
    assert xdict.is_alive is False
    assert entity.has_extension_dict is False


def test_link_dxf_object_to_extension_dict(doc):
    from ezdxf.entities import DXFObject

    xdict = ExtensionDict.new("ABBA", doc)
    owner = xdict.handle
    obj = DXFObject.new(handle="FEFE")
    xdict.link_dxf_object("MyEntry", obj)
    assert "MyEntry" in xdict
    assert obj.dxf.owner == owner
