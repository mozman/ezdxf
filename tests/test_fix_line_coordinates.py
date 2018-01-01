import pytest

from ezdxf.lldxf.repair import simple_tagger, fix_line_coordinate_order, fix_coordinates
from io import StringIO


def test_simple_tagger():
    tags = list(simple_tagger(StringIO(TEST_LINE1)))
    assert len(tags) == 14


def test_fix_line_coordinate_order():
    tags = list(simple_tagger(StringIO(TEST_LINE1)))
    ordered_tags = list(fix_line_coordinate_order(tags))
    assert ordered_tags[0] == (0, 'LINE')
    assert ordered_tags[-6] == (10, '1000.')
    assert ordered_tags[-5] == (20, '2000.')
    assert ordered_tags[-4] == (11, '1100.')
    assert ordered_tags[-3] == (21, '2100.')
    assert ordered_tags[-2] == (1000, 'ExtData')
    assert ordered_tags[-1] == (0, 'EOF')


def test_fix_2d_coordinates():
    ordered_tags = list(fix_coordinates(StringIO(TEST_LINE1)))
    assert ordered_tags[0] == (0, 'LINE')
    assert ordered_tags[-6] == (10, '1000.')
    assert ordered_tags[-5] == (20, '2000.')
    assert ordered_tags[-4] == (11, '1100.')
    assert ordered_tags[-3] == (21, '2100.')
    assert ordered_tags[-2] == (1000, 'ExtData')
    assert ordered_tags[-1] == (0, 'EOF')


def test_fix_invlaid_coordinates():
    # do not change invalid (missing) coordinates
    ordered_tags = list(fix_coordinates(StringIO(TEST_INVALID_LINE)))
    assert ordered_tags[0] == (0, 'LINE')
    assert ordered_tags[-5] == (10, '1000.')
    assert ordered_tags[-4] == (11, '1100.')
    assert ordered_tags[-3] == (21, '2100.')
    assert ordered_tags[-2] == (1000, 'ExtData')
    assert ordered_tags[-1] == (0, 'EOF')


def test_fix_3d_coordinates():
    ordered_tags = list(fix_coordinates(StringIO(TEST_3D_LINE)))
    assert ordered_tags[0] == (0, 'LINE')
    assert ordered_tags[-8] == (10, '1000.')
    assert ordered_tags[-7] == (20, '2000.')
    assert ordered_tags[-6] == (30, '3000.')
    assert ordered_tags[-5] == (11, '1100.')
    assert ordered_tags[-4] == (21, '2100.')
    assert ordered_tags[-3] == (31, '3100.')
    assert ordered_tags[-2] == (1000, 'ExtData')
    assert ordered_tags[-1] == (0, 'EOF')


TEST_LINE1 = """  0
LINE
  5
45
100
AcDbEntity
  8
4
  6
BYLAYER
 62
  256
370
   -1
100
AcDbLine
 10
1000.
 11
1100.
 20
2000.
 21
2100.
1000
ExtData
  0
EOF
"""

TEST_INVALID_LINE = """  0
LINE
  5
45
100
AcDbEntity
  8
4
  6
BYLAYER
 62
  256
370
   -1
100
AcDbLine
 10
1000.
 11
1100.
 21
2100.
1000
ExtData
  0
EOF
"""

TEST_3D_LINE = """  0
LINE
  5
45
100
AcDbEntity
  8
4
  6
BYLAYER
 62
  256
370
   -1
100
AcDbLine
 30
3000.
 31
3100.
 10
1000.
 11
1100.
 20
2000.
 21
2100.
1000
ExtData
  0
EOF
"""

if __name__ == '__main__':
    pytest.main([__file__])

