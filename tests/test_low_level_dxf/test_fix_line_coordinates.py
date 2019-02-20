from __future__ import unicode_literals

import pytest

from ezdxf.lldxf.tagger import low_level_tagger
from ezdxf.lldxf.repair import fix_coordinate_order, tag_reorder_layer
from io import StringIO


def string_reorder_tagger(s):
    return tag_reorder_layer(low_level_tagger(StringIO(s)))


def test_low_level_tagger():
    tags = list(low_level_tagger(StringIO(TEST_LINE1)))
    assert len(tags) == 14


def test_fix_line_coordinate_order():
    tags = list(low_level_tagger(StringIO(TEST_LINE1)))
    ordered_tags = list(fix_coordinate_order(tags, codes=(10, 11)))
    assert ordered_tags[0] == (0, 'LINE')
    assert ordered_tags[-6] == (10, '1000.')
    assert ordered_tags[-5] == (20, '2000.')
    assert ordered_tags[-4] == (11, '1100.')
    assert ordered_tags[-3] == (21, '2100.')
    assert ordered_tags[-2] == (1000, 'ExtData')
    assert ordered_tags[-1] == (0, 'EOF')


def test_fix_2d_coordinates():
    ordered_tags = list(string_reorder_tagger(TEST_LINE1))
    assert ordered_tags[0] == (0, 'LINE')
    assert ordered_tags[-6] == (10, '1000.')
    assert ordered_tags[-5] == (20, '2000.')
    assert ordered_tags[-4] == (11, '1100.')
    assert ordered_tags[-3] == (21, '2100.')
    assert ordered_tags[-2] == (1000, 'ExtData')
    assert ordered_tags[-1] == (0, 'EOF')


def test_dont_fix_invalid_coordinates():
    # do not change invalid (missing) coordinates
    ordered_tags = list(string_reorder_tagger(TEST_INVALID_LINE))
    assert ordered_tags[0] == (0, 'LINE')
    assert ordered_tags[-5] == (10, '1000.')
    assert ordered_tags[-4] == (11, '1100.')
    assert ordered_tags[-3] == (21, '2100.')
    assert ordered_tags[-2] == (1000, 'ExtData')
    assert ordered_tags[-1] == (0, 'EOF')


def test_fix_3d_coordinates():
    ordered_tags = list(string_reorder_tagger(TEST_3D_LINE))
    assert ordered_tags[0] == (0, 'LINE')
    assert ordered_tags[-8] == (10, '1000.')
    assert ordered_tags[-7] == (20, '2000.')
    assert ordered_tags[-6] == (30, '3000.')
    assert ordered_tags[-5] == (11, '1100.')
    assert ordered_tags[-4] == (21, '2100.')
    assert ordered_tags[-3] == (31, '3100.')
    assert ordered_tags[-2] == (1000, 'ExtData')
    assert ordered_tags[-1] == (0, 'EOF')


def test_fix_two_lines_coordinate_order():
    ordered_tags = list(string_reorder_tagger(TEST_TWO_LINES))
    assert len(ordered_tags) == 27
    assert ordered_tags[0] == (0, 'LINE')
    assert ordered_tags[-6] == (10, '1000.')
    assert ordered_tags[-5] == (20, '2000.')
    assert ordered_tags[-4] == (11, '1100.')
    assert ordered_tags[-3] == (21, '2100.')
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

TEST_TWO_LINES = """  0
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

if __name__ == '__main__':
    pytest.main([__file__])

