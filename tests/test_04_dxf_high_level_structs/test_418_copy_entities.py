#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.entities import Dictionary, Placeholder, LWPolyline


def test_copy_entity_with_extension_dict():
    doc = ezdxf.new()
    msp = doc.modelspace()
    entity = msp.add_point((0, 0))
    xdict = entity.new_extension_dict()
    placeholder = xdict.add_placeholder("Test")

    # recommended copy procedure:
    new_entity = doc.entitydb.duplicate_entity(entity)

    assert (
        new_entity.has_extension_dict is True
    ), "copied entity lost the extension dictionary"
    new_xdict = new_entity.get_extension_dict()
    new_dictionary = new_xdict.dictionary
    assert (
        new_dictionary is not xdict.dictionary
    ), "deep copy of the dictionary required"
    assert isinstance(new_dictionary, Dictionary) is True
    assert (
        new_dictionary in doc.objects
    ), "copied dictionary should be added to OBJECTS section"
    assert new_dictionary.dxf.owner == new_entity.dxf.handle

    new_placeholder = new_xdict["Test"]
    assert isinstance(new_placeholder, Placeholder)
    assert (
        new_placeholder is not placeholder
    ), "deep copy of the dictionary required"
    assert (
        new_placeholder in doc.objects
    ), "copied dictionary content should be added to OBJECTS section"


def test_virtual_copy_with_extension_dict():
    doc = ezdxf.new()
    msp = doc.modelspace()
    block = doc.blocks.new("TEST")
    entity = block.add_point((0, 0))
    xdict = entity.new_extension_dict()
    placeholder = xdict.add_placeholder("Test")

    insert = msp.add_blockref("TEST", (0, 0))
    count = len(doc.objects)
    # virtual entities are entity copies:
    new_entity = list(insert.virtual_entities())[0]

    assert (
        len(doc.objects) == count
    ), "virtual entities should not store new objects in the OBJECTS section"

    assert (
        new_entity.has_extension_dict is True
    ), "new entity lost the extension dictionary"
    new_xdict = new_entity.get_extension_dict()
    new_dictionary = new_xdict.dictionary

    # Problem of virtual entities:
    # The owner handle of the extension dictionary is None, because the entity
    # has no handle:
    assert new_entity.dxf.handle is None
    assert new_dictionary.dxf.owner is None

    # Adding the entity to a layout should fix this issue and also binds the
    # virtual extension dictionary to the document and add all dictionary
    # entries to the entity database and the OBJECTS section:
    msp.add_entity(new_entity)
    assert new_entity.dxf.handle is not None
    assert new_dictionary.dxf.owner == new_entity.dxf.handle

    assert (
        new_dictionary is not xdict.dictionary
    ), "deep copy of the dictionary required"
    assert isinstance(new_dictionary, Dictionary) is True
    assert (
        new_dictionary in doc.objects
    ), "copied dictionary should be added to OBJECTS section"
    assert new_dictionary.dxf.owner == new_entity.dxf.handle

    new_placeholder = new_xdict["Test"]
    assert isinstance(new_placeholder, Placeholder)
    assert (
        new_placeholder is not placeholder
    ), "deep copy of the dictionary required"
    assert (
        new_placeholder in doc.objects
    ), "copied dictionary content should be added to OBJECTS section"


def test_source_of_copy_for_bound_entity():
    doc = ezdxf.new()
    e = doc.modelspace().add_lwpolyline([(0, 0), (1, 0), (1, 1)])
    assert e.is_virtual is False

    c0 = e.copy()
    assert c0.is_virtual is True, "copy should be a virtual entity"
    assert c0.is_copy is True
    assert (
        c0.source_of_copy is e
    ), "should return the immediate source of the copy"
    assert (
        c0.origin_of_copy is e
    ), "should return the non virtual DXF entity as source of the copy"


def test_is_copy_state():
    doc = ezdxf.new()
    e = doc.modelspace().add_lwpolyline([(0, 0), (1, 0), (1, 1)])
    assert e.is_copy is False
    c0 = e.copy()
    assert c0.is_copy is True
    c1 = c0.copy()
    assert c1.is_copy is True


def test_origin_of_copy_for_copy_chains():
    doc = ezdxf.new()
    e = doc.modelspace().add_lwpolyline([(0, 0), (1, 0), (1, 1)])

    # first level copy
    c0 = e.copy()
    # second level copy
    c1 = c0.copy()
    assert (
        c1.source_of_copy is c0
    ), "should return the immediate source of the copy"
    assert (
        c1.origin_of_copy is e
    ), "should return the non virtual DXF entity as source of the copy"

    # third level copy
    c2 = c1.copy()
    assert (
        c2.source_of_copy is c1
    ), "should return the immediate source of the copy"
    assert (
        c2.origin_of_copy is e
    ), "should return the non virtual DXF entity as source of the copy"


def test_source_of_copy_for_virtual_entity():
    e = LWPolyline()
    e.vertices = [(0, 0), (1, 0), (1, 1)]
    assert e.is_virtual is True
    c = e.copy()
    assert c.is_virtual is True, "copy should be a virtual entity"
    assert c.is_copy is True, "should be a copy"
    assert (
        c.source_of_copy is e
    ), "should return the immediate source of the copy"
    assert (
        c.origin_of_copy is None
    ), "has no real DXF entity as source of the copy"


if __name__ == "__main__":
    pytest.main([__file__])
