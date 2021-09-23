# Copyright (c) 2011-2021, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf

from ezdxf.entities.dictionary import Dictionary, DictionaryWithDefault
from ezdxf.entities import DXFEntity, factory, DXFGraphic
from ezdxf import DXFKeyError, DXFValueError
from ezdxf.audit import Auditor, AuditError


class MockDoc:
    class MockEntityDB:
        def __getitem__(self, item):
            return item

    def __init__(self):
        self.entitydb = MockDoc.MockEntityDB()
        self.dxfversion = "AC1015"


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
