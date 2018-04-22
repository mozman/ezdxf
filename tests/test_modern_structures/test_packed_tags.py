# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.lldxf.packedtags import TagArray, TagDict
from ezdxf.lldxf.extendedtags import ExtendedTags

@pytest.fixture()
def numbers():
    return [1, 2, 3, 4]


def test_tag_array_init(numbers):
    array = TagArray(data=numbers)
    for index, value in enumerate(array.value):
        assert value == numbers[index]


def test_tag_array_dxf_tags(numbers):
    array = TagArray(data=numbers)
    tags = list(array.dxftags())
    assert len(tags) == len(numbers)
    for index, value in enumerate(tags):
        assert value == (TagArray.VALUE_CODE, numbers[index])


def test_tag_array_clone(numbers):
    array = TagArray(data=numbers)
    array2 = array.clone()
    array2.value[-1] = 9999
    assert array.value[:-1] == array2.value[:-1]
    assert array.value[-1] != array2.value[-1]


def test_inherited_array(numbers):
    class FloatArray(TagArray):
        VALUE_CODE = 40
        DTYPE = 'f'

    floats = FloatArray(data=numbers)
    for index, value in enumerate(floats.value):
        assert value == numbers[index]

    tags = list(floats.dxftags())
    for index, value in enumerate(tags):
        assert value == (FloatArray.VALUE_CODE, numbers[index])


@pytest.fixture()
def dict_data():
    return {
        'Name': 'mozman',
        'number': '4711',
        'handle': 'ABCDEF',
    }


def test_tag_dict_init(dict_data):
    d = TagDict()
    assert len(d.value) == 0

    d = TagDict(data=dict_data)
    assert d.value['Name'] == 'mozman'
    assert len(d.value) == len(dict_data)

    assert isinstance(d.value, dict)


def test_tag_dict_clone(dict_data):
    d1 = TagDict(dict_data)
    d2 = d1.clone()

    assert d1.value == d2.value
    d2.value['Name'] = 'test'
    assert d1.value != d2.value


def test_tag_dict_dxf_tags(dict_data):
    d = TagDict(dict_data)

    tags = list(d.dxftags())
    assert len(tags) == 6
    assert tags[0] == (3, 'Name')
    assert tags[1] == (350, 'mozman')
    assert tags[2] == (3, 'number')
    assert tags[3] == (350, '4711')
    assert tags[4] == (3, 'handle')
    assert tags[5] == (350, 'ABCDEF')


def test_dict_from_tags():
    root_dict = ExtendedTags.from_text(ROOTDICT)
    tags = root_dict.get_subclass('AcDbDictionary')
    d = TagDict.from_tags(tags)
    data = d.value
    assert len(data) == 14
    assert data['ACAD_MATERIAL'] == '72'

    assert len(tags) == 30
    d.replace_tags(tags)
    assert len(tags) == 3


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