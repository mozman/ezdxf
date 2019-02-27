# Created: 22.03.2011
# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf

from ezdxf.entities.dictionary import Dictionary, DictionaryWithDefault
from ezdxf import DXFKeyError


class MockDoc:
    class MockEntityDB:
        def __getitem__(self, item):
            return item

    def __init__(self):
        self.entitydb = MockDoc.MockEntityDB()


class TestNoneEmptyDXFDict:
    @pytest.fixture
    def dxfdict(self):
        d = Dictionary.from_text(ROOTDICT, doc=MockDoc())
        return d

    def test_getitem(self, dxfdict):
        assert dxfdict['ACAD_PLOTSTYLENAME'] == 'E'

    def test_len(self, dxfdict):
        assert 14 == len(dxfdict)

    def test_getitem_with_keyerror(self, dxfdict):
        with pytest.raises(ezdxf.DXFKeyError):
            _ = dxfdict['MOZMAN']

    def test_owner(self, dxfdict):
        assert dxfdict.dxf.owner == '0'

    def test_handle(self, dxfdict):
        assert dxfdict.dxf.handle == 'C'

    def test_get(self, dxfdict):
        assert dxfdict.get('ACAD_MOZMAN', 'XXX') == 'XXX'

    def test_get_entity(self, dxfdict):
        # returns just the handle, because no associated drawing exists
        assert 'E' == dxfdict.get('ACAD_PLOTSTYLENAME')

    def test_get_with_keyerror(self, dxfdict):
        with pytest.raises(ezdxf.DXFKeyError):
            _ = dxfdict.get('ACAD_MOZMAN')

    def test_contains(self, dxfdict):
        assert 'ACAD_PLOTSTYLENAME' in dxfdict

    def test_not_contains(self, dxfdict):
        assert 'MOZMAN' not in dxfdict

    def test_delete_existing_key(self, dxfdict):
        del dxfdict['ACAD_PLOTSTYLENAME']
        assert 'ACAD_PLOTSTYLENAME' not in dxfdict
        assert 13 == len(dxfdict)

    def test_delete_not_existing_key(self, dxfdict):
        with pytest.raises(ezdxf.DXFKeyError):
            del dxfdict['MOZMAN']

    def test_remove_existing_key(self, dxfdict):
        dxfdict.remove('ACAD_PLOTSTYLENAME')
        assert 'ACAD_PLOTSTYLENAME' not in dxfdict
        assert 13 == len(dxfdict)

    def test_remove_not_existing_key(self, dxfdict):
        with pytest.raises(ezdxf.DXFKeyError):
            dxfdict.remove('MOZMAN')

    def test_discard_existing_key(self, dxfdict):
        dxfdict.discard('ACAD_PLOTSTYLENAME')
        assert 'ACAD_PLOTSTYLENAME' not in dxfdict
        assert 13 == len(dxfdict)

    def test_discard_not_existing_key(self, dxfdict):
        dxfdict.discard('MOZMAN')
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
        dxfdict['TEST'] = "HANDLE"
        assert 1 == len(dxfdict)
        assert "HANDLE" == dxfdict['TEST']

    def test_add_first_item_2(self, dxfdict):
        dxfdict.add(key='TEST', value="HANDLE")
        assert 1 == len(dxfdict)
        assert "HANDLE" == dxfdict['TEST']

    def test_add_and_replace_first_item(self, dxfdict):
        dxfdict['TEST'] = "HANDLE"
        assert 1 == len(dxfdict)
        assert "HANDLE" == dxfdict['TEST']
        dxfdict['TEST'] = "HANDLE2"
        assert 1 == len(dxfdict)
        assert "HANDLE2" == dxfdict['TEST']

    def test_clear(self, dxfdict):
        assert 0 == len(dxfdict)
        dxfdict.clear()
        assert 0 == len(dxfdict)


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new2()


def test_get_entity_invalid_handle(doc):
    rootdict = doc.rootdict
    e = doc.dxffactory.new_entity('ACDBPLACEHOLDER', {})
    e.dxf.handle = 'FFFF'
    e.dxf.owner = 'ABBA'
    rootdict['TEST'] = e
    assert rootdict['TEST'].dxf.handle == 'FFFF'
    assert rootdict['TEST'].dxf.owner == 'ABBA'

    with pytest.raises(DXFKeyError):
        # just for testing, in production only DXFEntity() objects should be assigned
        rootdict['TEST'] = 'FFFF'

    with pytest.raises(DXFKeyError):
        _ = rootdict['MOZMAN']

    dxfdict = doc.rootdict.get_required_dict('TEST2')
    assert dxfdict.dxftype() == 'DICTIONARY', 'previous statement should not raise an exception'


def test_add_sub_dict(doc):
    rootdict = doc.rootdict
    assert 'MOZMAN_TEST' not in rootdict
    new_dict = rootdict.get_required_dict('MOZMAN_TEST')
    assert 'DICTIONARY' == new_dict.dxftype()
    assert 'MOZMAN_TEST' in rootdict


class TestDXFDictWithDefault:
    @pytest.fixture
    def dxfdict(self):
        return DictionaryWithDefault.from_text(DEFAULT_DICT, doc=MockDoc())

    def test_get_existing_value(self, dxfdict):
        assert 'F' == dxfdict['Normal']

    def test_get_not_existing_value(self, dxfdict):
        assert 'F' == dxfdict['Mozman']

    def test_get_default_value(self, dxfdict):
        assert 'F' == dxfdict.dxf.default

    def test_set_default_value(self, dxfdict):
        dxfdict.dxf.default = "MOZMAN"
        assert 'MOZMAN' == dxfdict['Mozman']


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
