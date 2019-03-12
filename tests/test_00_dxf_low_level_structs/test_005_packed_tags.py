# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.lldxf.packedtags import TagArray, VertexArray
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.tagwriter import TagCollector


@pytest.fixture()
def numbers():
    return [1, 2, 3, 4]


def test_tag_array_init(numbers):
    array = TagArray(data=numbers)
    for index, value in enumerate(array.values):
        assert value == numbers[index]


def test_tag_array_clone(numbers):
    array = TagArray(data=numbers)
    array2 = array.clone()
    array2.values[-1] = 9999
    assert array.values[:-1] == array2.values[:-1]
    assert array.values[-1] != array2.values[-1]


def test_inherited_array(numbers):
    class FloatArray(TagArray):
        DTYPE = 'f'

    floats = FloatArray(data=numbers)
    for index, value in enumerate(floats.values):
        assert value == numbers[index]


def test_vertex_array_basics():
    tags = ExtendedTags.from_text(SPLINE)
    vertices = VertexArray.from_tags(tags.get_subclass('AcDbSpline'))
    assert len(vertices) == 7
    points = list(vertices)
    assert len(points) == 7
    assert vertices[0] == (0., 0., 0.)
    assert vertices[1] == (10., 10., 10.)
    # test negative index
    assert vertices[-1] == (60., 60., 60.)
    with pytest.raises(IndexError):
        _ = vertices[-8]
    with pytest.raises(IndexError):
        _ = vertices[8]


def test_vertex_array_advanced():
    tags = ExtendedTags.from_text(SPLINE)
    vertices = VertexArray.from_tags(tags.get_subclass('AcDbSpline'))
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


def test_vertex_array_delete():
    tags = ExtendedTags.from_text(SPLINE)
    vertices = VertexArray.from_tags(tags.get_subclass('AcDbSpline'))
    assert len(vertices) == 7
    assert vertices[0] == (0, 0, 0)
    del vertices[0]
    assert vertices[0] == (10, 10, 10)
    assert len(vertices) == 6

    del vertices[1]  # (20, 20, 20)
    assert vertices[1] == (30, 30, 30)
    assert len(vertices) == 5


def test_vertex_array_delete_slices():
    tags = ExtendedTags.from_text(SPLINE)
    vertices = VertexArray.from_tags(tags.get_subclass('AcDbSpline'))
    del vertices[:2]
    assert len(vertices) == 5
    assert vertices[0] == (20, 20, 20)

    vertices = VertexArray.from_tags(tags.get_subclass('AcDbSpline'))
    del vertices[::2]
    assert len(vertices) == 3
    assert vertices[0] == (10, 10, 10)
    assert vertices[1] == (30, 30, 30)
    assert vertices[2] == (50, 50, 50)


def test_vertex_array_insert():
    tags = ExtendedTags.from_text(SPLINE)
    vertices = VertexArray.from_tags(tags.get_subclass('AcDbSpline'))
    assert vertices[0] == (0, 0, 0)
    assert vertices[1] == (10, 10, 10)
    vertices.insert(1, (-1, -2, -3))
    assert vertices[0] == (0, 0, 0)
    assert vertices[1] == (-1, -2, -3)
    assert vertices[2] == (10, 10, 10)
    assert len(vertices) == 8


def test_vertex_array_to_dxf_tags():
    tags = ExtendedTags.from_text(SPLINE)
    vertices = VertexArray.from_tags(tags.get_subclass('AcDbSpline'))
    tags = TagCollector.dxftags(vertices)
    assert len(tags) == 7*3
    assert tags[0] == (10,  0.)
    assert tags[3] == (10, 10.)
    assert tags[-1] == (30, 60.)


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