# Copyright (c) 2011-2022, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf

from ezdxf.entities import (
    Dictionary,
    DictionaryWithDefault,
    DictionaryVar,
    DXFEntity,
    factory,
    DXFGraphic,
    XRecord,
)

from ezdxf import DXFKeyError, DXFValueError
from ezdxf.audit import Auditor, AuditError


class MockDoc:
    class Objects:
        def delete_entity(self, entity):
            pass

    class EntityDB:
        def __getitem__(self, item):
            return item

    def __init__(self):
        self.entitydb = MockDoc.EntityDB()
        self.dxfversion = "AC1015"
        self.objects = MockDoc.Objects()


class TestNoneEmptyDXFDict:
    @pytest.fixture
    def dxfdict(self):
        d = Dictionary.from_text(ROOTDICT, doc=MockDoc())
        return d

    def test_getitem(self, dxfdict):
        assert dxfdict["ACAD_PLOTSTYLENAME"] == "E"

    def test_len(self, dxfdict):
        assert 14 == len(dxfdict)

    def test_getitem_with_keyerror(self, dxfdict):
        with pytest.raises(ezdxf.DXFKeyError):
            _ = dxfdict["MOZMAN"]

    def test_owner(self, dxfdict):
        assert dxfdict.dxf.owner == "0"

    def test_handle(self, dxfdict):
        assert dxfdict.dxf.handle == "C"

    def test_get(self, dxfdict):
        assert dxfdict.get("ACAD_MOZMAN", "XXX") == "XXX"

    def test_get_entity(self, dxfdict):
        # returns just the handle, because no associated drawing exists
        assert "E" == dxfdict.get("ACAD_PLOTSTYLENAME")

    def test_get_without_keyerror(self, dxfdict):
        assert dxfdict.get("ACAD_MOZMAN") is None

    def test_contains(self, dxfdict):
        assert "ACAD_PLOTSTYLENAME" in dxfdict

    def test_not_contains(self, dxfdict):
        assert "MOZMAN" not in dxfdict

    def test_delete_existing_key(self, dxfdict):
        del dxfdict["ACAD_PLOTSTYLENAME"]
        assert "ACAD_PLOTSTYLENAME" not in dxfdict
        assert 13 == len(dxfdict)

    def test_delete_not_existing_key(self, dxfdict):
        with pytest.raises(ezdxf.DXFKeyError):
            del dxfdict["MOZMAN"]

    def test_remove_existing_key(self, dxfdict):
        dxfdict.remove("ACAD_PLOTSTYLENAME")
        assert "ACAD_PLOTSTYLENAME" not in dxfdict
        assert 13 == len(dxfdict)

    def test_remove_not_existing_key(self, dxfdict):
        with pytest.raises(ezdxf.DXFKeyError):
            dxfdict.remove("MOZMAN")

    def test_discard_existing_key(self, dxfdict):
        dxfdict.discard("ACAD_PLOTSTYLENAME")
        assert "ACAD_PLOTSTYLENAME" not in dxfdict
        assert 13 == len(dxfdict)

    def test_discard_not_existing_key(self, dxfdict):
        dxfdict.discard("MOZMAN")
        assert 14 == len(dxfdict)

    def test_clear(self, dxfdict):
        assert 14 == len(dxfdict)
        dxfdict.clear()
        assert 0 == len(dxfdict)

    def test_keys(self, dxfdict):
        assert 14 == len(list(dxfdict.keys()))

    def test_items(self, dxfdict):
        assert 14 == len(list(dxfdict.items()))

    def test_find_key(self, dxfdict):
        entry = dxfdict["ACAD_COLOR"]
        assert dxfdict.find_key(entry) == "ACAD_COLOR"


class TestEmptyDXFDict:
    @pytest.fixture
    def dxfdict(self):
        return Dictionary.from_text(EMPTY_DICT, doc=MockDoc())

    def test_len(self, dxfdict):
        assert 0 == len(dxfdict)

    def test_add_first_item(self, dxfdict):
        dxfdict["TEST"] = "ABBA"
        assert 1 == len(dxfdict)
        assert "ABBA" == dxfdict["TEST"]

    def test_add_first_item_2(self, dxfdict):
        dxfdict.add("TEST", "ABBA")
        assert 1 == len(dxfdict)
        assert "ABBA" == dxfdict["TEST"]

    def test_add_and_replace_first_item(self, dxfdict):
        dxfdict["TEST"] = "ABBA"
        assert 1 == len(dxfdict)
        assert "ABBA" == dxfdict["TEST"]
        dxfdict["TEST"] = "FEFE"
        assert 1 == len(dxfdict)
        assert "FEFE" == dxfdict["TEST"]

    def test_clear(self, dxfdict):
        assert 0 == len(dxfdict)
        dxfdict.clear()
        assert 0 == len(dxfdict)


@pytest.fixture(scope="module")
def doc():
    return ezdxf.new()


def test_do_not_recover_owner_tag_at_loading_stage():
    # this is the task of the audit process and breaks otherwise the
    # recover mode for test file: "ProE_AC1018.dxf"
    d = Dictionary.from_text(WITHOUT_OWNER_TAG)
    assert d.dxf.hasattr("owner") is False


def test_dictionary_loads_owner_tag():
    d = Dictionary.from_text(WITH_OWNER_TAG)
    assert d.dxf.owner == "FEFE"


def test_get_entity_invalid_handle(doc):
    rootdict = doc.rootdict
    e = factory.new("ACDBPLACEHOLDER", {})
    e.dxf.handle = "FFFF"
    e.dxf.owner = "ABBA"
    rootdict["TEST"] = e
    assert rootdict["TEST"].dxf.handle == "FFFF"
    assert rootdict["TEST"].dxf.owner == "ABBA"

    with pytest.raises(DXFValueError):
        rootdict["TEST"] = "XXX"

    with pytest.raises(DXFKeyError):
        _ = rootdict["MOZMAN"]

    dxfdict = doc.rootdict.get_required_dict("TEST2")
    assert (
        dxfdict.dxftype() == "DICTIONARY"
    ), "previous statement should not raise an exception"


def test_add_sub_dict(doc):
    rootdict = doc.rootdict
    assert "MOZMAN_TEST" not in rootdict
    new_dict = rootdict.get_required_dict("MOZMAN_TEST")
    assert "DICTIONARY" == new_dict.dxftype()
    assert "MOZMAN_TEST" in rootdict
    assert new_dict.dxf.owner == rootdict.dxf.handle


class TestDictionaryVar:
    def test_add_dict_var(self, doc):
        rootdict = doc.rootdict
        assert "MOZMAN_VAR" not in rootdict
        new_var = rootdict.add_dict_var("MOZMAN_VAR", "Hallo")
        assert new_var.dxftype() == "DICTIONARYVAR"
        assert "MOZMAN_VAR" in rootdict
        assert new_var.dxf.value == "Hallo"
        assert new_var.dxf.owner == rootdict.dxf.handle

    def test_value_property(self, doc):
        rootdict = doc.rootdict
        new_var = rootdict.add_dict_var("MOZMAN_VAR2", "")
        assert new_var.value == ""
        new_var.value = "Hello"
        assert new_var.value == "Hello"


def test_add_xrecord(doc):
    rootdict = doc.rootdict
    assert "MOZMAN_XRECORD" not in rootdict
    xrecord = rootdict.add_xrecord("MOZMAN_XRECORD")
    assert xrecord.dxftype() == "XRECORD"
    assert "MOZMAN_XRECORD" in rootdict
    assert xrecord.dxf.owner == rootdict.dxf.handle


def test_cannot_add_graphical_entities_to_dict(doc):
    line = doc.modelspace().add_line((0, 0), (10, 0))
    assert isinstance(line, DXFGraphic)
    with pytest.raises(ezdxf.DXFTypeError):
        doc.rootdict["LINE"] = line


def test_audit_fix_invalid_root_dict_owner():
    doc = ezdxf.new()
    rootdict = doc.rootdict
    auditor = Auditor(doc)

    rootdict.dxf.owner = "FF"  # set invalid owner
    auditor.run()
    assert len(auditor.fixes) == 1
    assert auditor.fixes[0].code == AuditError.INVALID_OWNER_HANDLE
    assert rootdict.dxf.owner == "0"


def test_audit_ok():
    doc = ezdxf.new()
    auditor = Auditor(doc)

    rootdict = doc.rootdict
    assert "TEST_VAR_1" not in rootdict
    new_var = rootdict.add_dict_var("TEST_VAR_1", "Hallo")
    assert new_var.dxftype() == "DICTIONARYVAR"

    rootdict.audit(auditor)
    assert len(auditor) == 0


def test_audit_invalid_pointer():
    doc = ezdxf.new()
    auditor = Auditor(doc)

    d = doc.rootdict.add_new_dict("TEST_AUDIT_2")
    entry = d.add_dict_var("TEST_VAR_2", "Hallo")
    entry.dxf.handle = "ABBA"
    d.audit(auditor)
    assert len(auditor.fixes) == 1
    e = auditor.fixes[0]
    assert e.code == AuditError.INVALID_DICTIONARY_ENTRY


def test_audit_fix_invalid_pointer():
    doc = ezdxf.new()
    auditor = Auditor(doc)

    d = doc.rootdict.add_new_dict("TEST_AUDIT_3")
    entry = d.add_dict_var("TEST_VAR_3", "Hallo")
    entry.dxf.handle = "ABBA"
    d.audit(auditor)
    assert len(auditor) == 0, "should return count of unfixed errors"
    assert len(auditor.errors) == 0
    assert len(auditor.fixes) == 1
    fix = auditor.fixes[0]
    assert fix.code == AuditError.INVALID_DICTIONARY_ENTRY

    # test if invalid entry was removed
    assert len(d) == 0
    assert "TEST_VAR_3" not in d


def test_audit_restores_deleted_owner_tag():
    doc = ezdxf.new()
    d = doc.objects.add_dictionary()
    d.dxf.discard("owner")
    auditor = Auditor(doc)
    d.audit(auditor)
    assert d.dxf.owner == doc.rootdict.dxf.handle, "assign to root dict"


def test_link_dxf_object_to_dictionary():
    from ezdxf.entities import DXFObject

    dictionary = Dictionary.new(handle="ABBA")
    obj = DXFObject.new(handle="FEFE")
    dictionary.link_dxf_object("MyEntry", obj)
    assert "MyEntry" in dictionary
    assert obj.dxf.owner == "ABBA"


class TestDXFDictWithDefault:
    @pytest.fixture
    def dxfdict(self):
        d = DictionaryWithDefault.from_text(DEFAULT_DICT, doc=MockDoc())
        d._default = DXFEntity()
        d._default.dxf.handle = "FEFE"
        return d

    def test_get_existing_value(self, dxfdict):
        assert "F" == dxfdict["Normal"]

    def test_get_not_existing_value(self, dxfdict):
        assert dxfdict["Mozman"].dxf.handle == "FEFE"

    def test_get_default_value(self, dxfdict):
        assert "F" == dxfdict.dxf.default

    def test_set_default_value(self, dxfdict):
        e = DXFEntity()
        e.dxf.handle = "ABBA"

        dxfdict.set_default(e)
        assert dxfdict["Mozman"].dxf.handle == "ABBA"

    def test_create_place_holder_for_invalid_default_vaue(self):
        doc = ezdxf.new()
        d = doc.objects.add_dictionary_with_default(
            owner=doc.rootdict.dxf.handle, default="0"
        )
        auditor = Auditor(doc)
        d.audit(auditor)
        default = d.get("xxx")
        assert default.is_alive is True
        assert default.dxftype() == "ACDBPLACEHOLDER"


class TestCopyHardOwnerDictionary:
    @pytest.fixture(scope="class")
    def source(self, doc) -> Dictionary:
        doc = ezdxf.new()
        dictionary = doc.rootdict.get_required_dict("COPYTEST", hard_owned=True)
        dictionary.add_dict_var("DICTVAR", "VarContent")
        xrecord = dictionary.add_xrecord("XRECORD")
        xrecord.reset([(1, "String"), (40, 3.1415), (90, 4711)])
        return dictionary

    def test_keys_are_copied(self, source: Dictionary):
        copy = source.copy()
        assert "DICTVAR" in copy
        assert "XRECORD" in copy

    def test_objects_exist(self, source: Dictionary):
        copy = source.copy()
        assert isinstance(copy["DICTVAR"], DictionaryVar)
        assert isinstance(copy["XRECORD"], XRecord)

    def test_objects_are_copied(self, source: Dictionary):
        copy = source.copy()
        assert copy["DICTVAR"] is not source["DICTVAR"]
        assert copy["XRECORD"] is not source["XRECORD"]

    def test_copied_objects_are_not_bound_to_document(self, source: Dictionary):
        copy = source.copy()
        assert factory.is_bound(copy["DICTVAR"], source.doc) is False
        assert factory.is_bound(copy["XRECORD"], source.doc) is False

    def test_fully_manual_dictionary_copy(self, source: Dictionary):
        doc = source.doc
        # manual copy procedure:
        copy = source.copy()
        factory.bind(copy, doc)
        doc.objects.add_object(copy)
        # this is all done automatically if you use:
        # doc.entitydb.duplicate_entity(source)
        assert copy in doc.objects
        assert factory.is_bound(copy, doc)

    @pytest.mark.parametrize("key", ["DICTVAR", "XRECORD"])
    def test_copied_data_is_bound(self, source: Dictionary, key: str):
        doc = source.doc
        copy = doc.entitydb.duplicate_entity(source)
        source_handle = source[key].dxf.handle
        copied_handle = copy[key].dxf.handle
        assert copied_handle is not None
        assert source_handle != copied_handle
        assert copied_handle in doc.entitydb
        assert copy[key] in doc.objects
        assert factory.is_bound(copy[key], doc)

    def test_copied_xrecord(self, source: Dictionary):
        doc = source.doc
        copy = doc.entitydb.duplicate_entity(source)
        xrecord = copy["XRECORD"]
        assert xrecord.tags == [(1, "String"), (40, 3.1415), (90, 4711)]

    def test_copied_objects_are_owned_by_copy(self, source: Dictionary):
        copy = source.copy()
        assert copy["DICTVAR"].dxf.owner == copy.dxf.handle
        assert copy["XRECORD"].dxf.owner == copy.dxf.handle

    def test_copy_sub_dictionary(self, source: Dictionary):
        doc = source.doc
        source = doc.entitydb.duplicate_entity(source)
        sub_dict = source.add_new_dict("SUBDICT", hard_owned=True)
        sub_dict.add_dict_var("SUBDICTVAR", "SubVarContent")
        copy = doc.entitydb.duplicate_entity(source)

        sub_dict_copy = copy["SUBDICT"]
        assert sub_dict is not sub_dict_copy
        assert sub_dict["SUBDICTVAR"] is not sub_dict_copy["SUBDICTVAR"]
        assert factory.is_bound(sub_dict_copy, doc) is True
        assert factory.is_bound(sub_dict_copy["SUBDICTVAR"], doc) is True


class TestCopyNotHardOwnerDictionary:
    @pytest.fixture(scope="class")
    def source(self, doc) -> Dictionary:
        doc = ezdxf.new()
        dictionary = doc.rootdict.get_required_dict("COPYTEST", hard_owned=True)
        dict_var = dictionary.add_dict_var("DICTVAR", "VarContent")
        xrecord = dictionary.add_xrecord("XRECORD")
        xrecord.reset([(1, "String"), (40, 3.1415), (90, 4711)])
        dictionary2 = doc.rootdict.get_required_dict("COPYTEST2", hard_owned=False)
        dictionary2["DICTVAR"] = dict_var
        dictionary2["XRECORD"] = xrecord
        return dictionary2

    def test_is_not_hard_owner(self, source: Dictionary):
        assert source.is_hard_owner is False

    def test_keys_are_copied(self, source: Dictionary):
        copy = source.copy()
        assert "DICTVAR" in copy
        assert "XRECORD" in copy

    def test_objects_exist(self, source: Dictionary):
        copy = source.copy()
        assert isinstance(copy["DICTVAR"], DictionaryVar)
        assert isinstance(copy["XRECORD"], XRecord)

    def test_objects_are_not_copied(self, source: Dictionary):
        copy = source.copy()
        assert copy["DICTVAR"] is source["DICTVAR"]
        assert copy["XRECORD"] is source["XRECORD"]

    def test_objects_are_not_owned_by_copy(self, source: Dictionary):
        copy = source.copy()
        assert copy["DICTVAR"].dxf.owner != copy.dxf.handle
        assert copy["XRECORD"].dxf.owner != copy.dxf.handle

    def test_copied_dictionary_is_bound(self, source: Dictionary):
        doc = source.doc
        copy = doc.entitydb.duplicate_entity(source)
        assert copy in doc.objects
        assert factory.is_bound(copy, doc)


ROOTDICT = """0
DICTIONARY
5
C
330
0
100
AcDbDictionary
281
1
3
ACAD_COLOR
350
73
3
ACAD_GROUP
350
D
3
ACAD_LAYOUT
350
1A
3
ACAD_MATERIAL
350
72
3
ACAD_MLEADERSTYLE
350
D7
3
ACAD_MLINESTYLE
350
17
3
ACAD_PLOTSETTINGS
350
19
3
ACAD_PLOTSTYLENAME
350
E
3
ACAD_SCALELIST
350
B6
3
ACAD_TABLESTYLE
350
86
3
ACAD_VISUALSTYLE
350
99
3
ACDB_RECOMPOSE_DATA
350
40F
3
AcDbVariableDictionary
350
66
3
DWGPROPS
350
410
"""

EMPTY_DICT = """  0
DICTIONARY
  5
C
330
0
100
AcDbDictionary
281
     1
"""

DEFAULT_DICT = """  0
ACDBDICTIONARYWDFLT
  5
E
102
{ACAD_REACTORS
330
C
102
}
330
C
100
AcDbDictionary
281
     1
  3
Normal
350
F
100
AcDbDictionaryWithDefault
340
F
"""

WITHOUT_OWNER_TAG = """0
DICTIONARY
5
C
100
AcDbDictionary
281
1
"""

WITH_OWNER_TAG = """0
DICTIONARY
5
C
330
FEFE
100
AcDbDictionary
281
1
"""
