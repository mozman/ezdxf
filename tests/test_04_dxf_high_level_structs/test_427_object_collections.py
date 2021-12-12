#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
"""
Test the ezdxf.entities.objectcollection module, but the tests need
a real implementation: MLeaderStyleCollection

"""
import pytest

import ezdxf
from ezdxf.entities import is_dxf_object


@pytest.fixture(scope="module")
def collection_ro():
    """Creates a read only document"""
    doc = ezdxf.new()
    doc.entitydb.locked = True
    return doc.mleader_styles


class TestGetterMethods:
    def test_len(self, collection_ro):
        assert len(collection_ro) == 1

    def test_iter(self, collection_ro):
        assert len(list(collection_ro)) == 1

    def test_is_unique_name(self, collection_ro):
        assert collection_ro.is_unique_name("STANDARD") is False

    def test_contains(self, collection_ro):
        assert ("Standard" in collection_ro) is True

    def test_contains_is_case_insensitive(self, collection_ro):
        assert ("STANDARD" in collection_ro) is True

    def test_getitem(self, collection_ro):
        assert collection_ro["Standard"].dxf.name == "Standard"

    def test_getitem_is_case_insensitive(self, collection_ro):
        assert collection_ro["STANDARD"].dxf.name == "Standard"

    def test_get(self, collection_ro):
        assert collection_ro.get("Standard").dxf.name == "Standard"

    def test_get_is_case_insensitive(self, collection_ro):
        assert collection_ro.get("STANDARD").dxf.name == "Standard"


@pytest.fixture(scope="module")
def collection_rw():
    doc = ezdxf.new()
    return doc.mleader_styles


class TestCreateNewEntry:
    def test_new_entry_is_an_object(self, collection_rw):
        obj = collection_rw.new("New1")
        assert is_dxf_object(obj) is True
        assert obj.dxf.name == "New1"

    def test_new_entry_is_added_to_collection(self, collection_rw):
        count = len(collection_rw)
        collection_rw.new("New2")
        assert len(collection_rw) == count + 1
        assert "NEW2" in collection_rw, "case insensitive names"

    def test_cannot_use_existing_name(self, collection_rw):
        collection_rw.new("New3")
        with pytest.raises(ValueError):
            collection_rw.new("NEW3"), "case insensitive names"


class TestDeleteEntry:
    def test_delete_entry_remove_entry(self, collection_rw):
        count = len(collection_rw)
        collection_rw.new("Del1")
        collection_rw.delete("DEL1")
        assert len(collection_rw) == count

    def test_delete_non_existing_entry_does_not_raise_exception(
        self, collection_rw
    ):
        count = len(collection_rw)
        collection_rw.delete("DEL2")
        assert len(collection_rw) == count


class TestDuplicateEntry:
    def test_duplicate_existing_entry(self, collection_rw):
        count = len(collection_rw)
        obj = collection_rw.duplicate_entry("STANDARD", "Dup1")
        assert is_dxf_object(obj) is True
        assert obj.dxf.name == "Dup1"
        assert len(collection_rw) == count + 1

    def test_duplicate_non_existing_entry_raises_exception(self, collection_rw):
        with pytest.raises(ValueError):
            collection_rw.duplicate_entry("NON_EXISTING_ENTRY", "Dup1")

    def test_new_entry_replaces_existing_entry(self, collection_rw):
        count = len(collection_rw)
        obj1 = collection_rw.duplicate_entry("STANDARD", "Dup2")
        obj2 = collection_rw.duplicate_entry("Standard", "DUP2")
        assert obj1 is not obj2, "obj2 must be a new object"
        assert collection_rw.get("Dup2") is obj2, "obj2 should replace obj1"
        assert len(collection_rw) == count + 1


def test_clear():
    doc = ezdxf.new()
    doc.mleader_styles.clear()
    # This creates an invalid DXF file!!!
    assert len(doc.mleader_styles) == 0


if __name__ == "__main__":
    pytest.main([__file__])
