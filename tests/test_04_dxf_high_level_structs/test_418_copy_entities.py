#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.entities import Dictionary, Placeholder


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


if __name__ == "__main__":
    pytest.main([__file__])
