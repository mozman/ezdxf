# Copyright (c) 2018-2019 Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.types import is_embedded_object_marker
from ezdxf.entities.mtext import MText
MTEXT = r"""0
MTEXT
5
278
330
1F
100
AcDbEntity
8
0
100
AcDbMText
10
2762.147
20
2327.073
30
0.0
40
2.5
41
18.851
46
0.0
71
1
72
5
1
{\fArial|b0|i0|c162|p34;CHANGE;\P\P\PTEXT}
73
1
44
1.0
101
Embedded Object
70
1
10
1.0
20
0.0
30
0.0
11
2762.147
21
2327.073
31
0.0
40
18.851
41
0.0
42
15.428
43
15.042
71
2
72
1
44
18.851
45
12.5
73
0
74
0
46
0.0
"""


@pytest.fixture
def mtext_tags():
    return ExtendedTags.from_text(MTEXT)


def test_parse_embedded_object(mtext_tags):
    tags = mtext_tags
    assert tags.embedded_objects is not None
    assert len(tags.embedded_objects) == 1


def test_embedded_object_structure(mtext_tags):
    emb_obj = mtext_tags.embedded_objects[0]
    assert is_embedded_object_marker(emb_obj[0])
    assert len(emb_obj) == 15
    assert emb_obj[-1] == (46, 0.)


def test_mtext_structure(mtext_tags):
    assert len(mtext_tags.subclasses[2]) == 10

    mtext = MText.from_text(MTEXT)
    assert mtext.dxf.handle == '278'
    assert mtext.dxf.line_spacing_factor == 1.0


def test_mtext_set_text(mtext_tags):
    mtext = MText.from_text(MTEXT)
    mtext.set_text('Hello?')
    assert mtext.get_text() == 'Hello?'
    assert mtext.dxf.line_spacing_factor == 1.0
    assert len(mtext.embedded_objects.embedded_objects[0]) == 15


@pytest.fixture
def two_embedded_objects():
    return ExtendedTags.from_text("""0
TEST
5
FFFF
101
Embedded Object
1
Text
101
Embedded Object
2
Text2
""")


def test_two_embedded_objects(two_embedded_objects):
    tags = two_embedded_objects
    assert len(tags.embedded_objects) == 2

    emb_obj = tags.embedded_objects[0]
    assert is_embedded_object_marker(emb_obj[0])
    assert emb_obj[1] == (1, 'Text')

    emb_obj = tags.embedded_objects[1]
    assert is_embedded_object_marker(emb_obj[0])
    assert emb_obj[1] == (2, 'Text2')


def test_iter_tags(two_embedded_objects):
    tags = two_embedded_objects
    flat_tags = list(tags)
    assert len(flat_tags) == 6
    assert flat_tags[0] == (0, 'TEST')
    assert flat_tags[-1] == (2, 'Text2')
