# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.lldxf.packedtags import TagArray, TagDict, VertexTags
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


def test_empty_tag_array_dxf_tags():
    array = TagArray()
    tags = list(array.dxftags())
    assert len(tags) == 0
    assert array.dxfstr() == ''


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


def test_vertex_tags_basics():
    tags = ExtendedTags.from_text(SPLINE)
    vertices = VertexTags.from_tags(tags.get_subclass('AcDbSpline'))
    assert len(vertices) == 7
    points = list(vertices)
    assert len(points) == 7
    assert vertices[0] == (0., 0., 0.)
    assert vertices[1] == (10., 10., 10.)
    # test negative index
    assert vertices[-1] == (60., 60., 60.)
    with pytest.raises(IndexError):
        vertices[-8]
    with pytest.raises(IndexError):
        vertices[8]


def test_vertex_tags_advanced():
    tags = ExtendedTags.from_text(SPLINE)
    vertices = VertexTags.from_tags(tags.get_subclass('AcDbSpline'))
    # append()
    vertices.append((70, 70, 70))
    assert len(vertices) == 8
    assert vertices[-1] == (70., 70., 70.)

    # set vertex
    vertices[0] = (7, 6, 5)
    assert vertices[0] == (7, 6, 5)
    assert len(vertices) == 8

    # clear()
    vertices.clear()
    assert len(vertices) == 0

    # extend()
    vertices.extend([(0, 0, 0), (1, 2, 3), (4, 5, 6)])
    assert len(vertices) == 3
    assert vertices[0] == (0, 0, 0)
    assert vertices[1] == (1, 2, 3)
    assert vertices[2] == (4, 5, 6)


def test_vertex_tags_delete():
    tags = ExtendedTags.from_text(SPLINE)
    vertices = VertexTags.from_tags(tags.get_subclass('AcDbSpline'))
    assert len(vertices) == 7
    assert vertices[0] == (0, 0, 0)
    del vertices[0]
    assert vertices[0] == (10, 10, 10)
    assert len(vertices) == 6

    del vertices[1]  # (20, 20, 20)
    assert vertices[1] == (30, 30, 30)
    assert len(vertices) == 5


def test_vertex_tags_delete_slices():
    tags = ExtendedTags.from_text(SPLINE)
    vertices = VertexTags.from_tags(tags.get_subclass('AcDbSpline'))
    del vertices[:2]
    assert len(vertices) == 5
    assert vertices[0] == (20, 20, 20)

    vertices = VertexTags.from_tags(tags.get_subclass('AcDbSpline'))
    del vertices[::2]
    assert len(vertices) == 3
    assert vertices[0] == (10, 10, 10)
    assert vertices[1] == (30, 30, 30)
    assert vertices[2] == (50, 50, 50)


def test_vertex_tags_insert():
    tags = ExtendedTags.from_text(SPLINE)
    vertices = VertexTags.from_tags(tags.get_subclass('AcDbSpline'))
    assert vertices[0] == (0, 0, 0)
    assert vertices[1] == (10, 10, 10)
    vertices.insert(1, (-1, -2, -3))
    assert vertices[0] == (0, 0, 0)
    assert vertices[1] == (-1, -2, -3)
    assert vertices[2] == (10, 10, 10)
    assert len(vertices) == 8


def test_vertex_tags_to_dxf_tags():
    tags = ExtendedTags.from_text(SPLINE)
    vertices = VertexTags.from_tags(tags.get_subclass('AcDbSpline'))
    tags = list(vertices.dxftags())
    assert len(tags) == 7
    assert tags[0] == (10, (0., 0., 0.))
    assert tags[1] == (10, (10., 10., 10.))
    assert tags[-1] == (10, (60., 60., 60.))


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

SPLINE = """0
SPLINE
5
697
102
{ACAD_REACTORS
330
6E8
102
}
330
1F
100
AcDbEntity
8
1
370
20
100
AcDbSpline
210
0.0
220
0.0
230
1.0
70
8
71
3
72
11
73
7
74
0
42
0.000000001
43
0.0000000001
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
40
2.0
40
3.0
40
3.0
40
3.0
40
3.0
40
3.0
10
0.0
20
0.0
30
0.0
10
10.
20
10.
30
10.
10
20.
20
20.
30
20.
10
30.
20
30.
30
30.
10
40.
20
40.
30
40.
10
50.
20
50.
30
50.
10
60.
20
60.
30
60.
"""