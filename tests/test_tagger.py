from __future__ import unicode_literals
import pytest
from io import StringIO

from ezdxf.lldxf.tagger import internal_tag_compiler, skip_comments,low_level_tagger, tag_compiler, DXFStructureError
from ezdxf.lldxf.tags import DXFTag
from ezdxf.lldxf.types import strtag


def test_strtag_int():
    assert '  1\n1\n' == strtag((1, 1))


def test_strtag_float():
    assert ' 10\n3.1415\n' == strtag((10, 3.1415))


def test_strtag_str():
    assert '  0\nSECTION\n' == strtag((0, 'SECTION'))


def test_int_not_skip_comments():
    tags = list(internal_tag_compiler(TAGS1))
    assert 9 == len(tags)
    assert DXFTag(999, 'comment') == tags[0]


def test_int_skip_comments():
    comments = []
    tags = list(skip_comments(internal_tag_compiler(TAGS1), comments))
    assert 8 == len(tags)
    assert 'comment' == comments[0]


def test_int_3d_coords():
    tags = list(internal_tag_compiler(TAGS_3D_COORDS))
    assert 2 == len(tags)
    assert DXFTag(10, (100, 200, 300)) == tags[1]


def test_int_2d_coords():
    tags = list(internal_tag_compiler(TAGS_2D_COORDS))
    assert 2 == len(tags)
    assert DXFTag(10, (100, 200)) == tags[1]


def test_int_multiple_2d_coords():
    tags = list(internal_tag_compiler(TAGS_2D_COORDS2))
    assert 3 == len(tags)
    assert DXFTag(10, (100, 200)) == tags[1]
    assert DXFTag(11, (1000, 2000)) == tags[2]


def test_int_no_line_break_at_eof():
    tags = list(internal_tag_compiler(TAGS_NO_LINE_BREAK_AT_EOF))
    assert 3 == len(tags)
    assert DXFTag(10, (100, 200)) == tags[1]
    assert DXFTag(11, (1000, 2000)) == tags[2]


def test_int_float_to_int():
    with pytest.raises(ValueError):
        # Floats as int not allowed for internal tag compiler.
        list(internal_tag_compiler(FLOAT_FOR_INT_TAGS))


def test_int_no_eof():
    tags = list(internal_tag_compiler(TEST_NO_EOF))
    assert 7 == len(tags)
    assert (0, 'ENDSEC') == tags[-1]


def external_tag_compiler(text):
    return tag_compiler(low_level_tagger(StringIO(text)))


@pytest.fixture
def reader():
    return external_tag_compiler(TEST_TAGREADER)


def test_ext_next(reader):
    assert (0, 'SECTION') == next(reader)


def test_ext_to_list(reader):
    assert 8 == len(list(reader))


def test_ext_one_point_reader():
    tags = list(external_tag_compiler(POINT_TAGS))
    point_tag = tags[1]
    assert (100, 200, 300) == point_tag.value


def test_ext_read_2D_points():
    stri = internal_tag_compiler(POINT_2D_TAGS)
    tags = list(stri)
    tag = tags[0]  # 2D point
    assert (100, 200) == tag.value
    tag = tags[1]  # check mark
    assert 'check mark 1' == tag.value
    tag = tags[2]  # 3D point
    assert (100, 200, 300) == tag.value
    tag = tags[3]  # check mark
    assert 'check mark 2' == tag.value


def test_ext_error_tag():
    tags = list(external_tag_compiler(TAGS_WITH_ERROR))
    assert 1 == len(tags)


def test_ext_float_to_int():
    # Floats as int allowed for external tag compiler (thx ProE).
    assert list(external_tag_compiler(FLOAT_FOR_INT_TAGS))[0] == (71, 1)


def test_ext_coord_error_tag():
    with pytest.raises(DXFStructureError):
        list(external_tag_compiler(TAGS_WITH_COORD_ERROR))


TAGS1 = """999
comment
  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1018
  9
$DWGCODEPAGE
  3
ANSI_1252
  0
ENDSEC
  0
EOF
"""

TAGS_3D_COORDS = """  9
$EXTMIN
 10
100
 20
200
 30
300
"""

TAGS_2D_COORDS = """  9
$EXTMIN
 10
100
 20
200
"""

TAGS_2D_COORDS2 = """  9
$EXTMIN
 10
100
 20
200
 11
1000
 21
2000
"""

TAGS_NO_LINE_BREAK_AT_EOF = """  9
$EXTMIN
 10
100
 20
200
 11
1000
 21
2000"""


TEST_TAGREADER = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1018
  9
$DWGCODEPAGE
  3
ANSI_1252
  0
ENDSEC
  0
EOF
"""

TEST_NO_EOF = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1018
  9
$DWGCODEPAGE
  3
ANSI_1252
  0
ENDSEC
"""

TEST_TAGREADER_COMMENTS = """999
Comment0
  0
SECTION
  2
HEADER
  9
$ACADVER
999
Comment1
  1
AC1018
  9
$DWGCODEPAGE
  3
ANSI_1252
  0
ENDSEC
  0
EOF
"""

POINT_TAGS = """  9
$EXTMIN
 10
100
 20
200
 30
300
"""

POINT_2D_TAGS = """ 10
100
 20
200
  9
check mark 1
 10
100
 20
200
 30
300
  9
check mark 2
"""

FLOAT_FOR_INT_TAGS = """  71
1.0
"""

TAGS_WITH_ERROR = """  9
$EXTMIN
 10
100
 20
"""

TAGS_WITH_COORD_ERROR = """  9
$EXTMIN
 20
100
 10
100
 40
1.0  
"""

