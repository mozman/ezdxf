from __future__ import unicode_literals
import unittest
from io import StringIO

from ezdxf.lldxf.tagger import internal_tag_compiler, skip_comments,low_level_tagger, tag_compiler
from ezdxf.lldxf.tags import DXFTag
from ezdxf.lldxf.types import strtag


def optimizing_stream_tagger(stream):
    return tag_compiler(low_level_tagger(stream))


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


class TestTrustedStringTagger(unittest.TestCase):
    def test_string(self):
        tags = list(internal_tag_compiler(TAGS1))
        self.assertEqual(9, len(tags))
        self.assertEqual(DXFTag(999, 'comment'), tags[0], 'should not skip comments.')

    def test_skip_comments(self):
        comments = []
        tags = list(skip_comments(internal_tag_compiler(TAGS1), comments))
        self.assertEqual(8, len(tags))
        self.assertEqual('comment', comments[0])

    def test_3d_coords(self):
        tags = list(internal_tag_compiler(TAGS_3D_COORDS))
        self.assertEqual(2, len(tags))
        self.assertEqual(DXFTag(10, (100, 200, 300)), tags[1])

    def test_2d_coords(self):
        tags = list(internal_tag_compiler(TAGS_2D_COORDS))
        self.assertEqual(2, len(tags))
        self.assertEqual(DXFTag(10, (100, 200)), tags[1])

    def test_multiple_2d_coords(self):
        tags = list(internal_tag_compiler(TAGS_2D_COORDS2))
        self.assertEqual(3, len(tags))
        self.assertEqual(DXFTag(10, (100, 200)), tags[1])
        self.assertEqual(DXFTag(11, (1000, 2000)), tags[2])

    def test_no_line_break_at_eof(self):
        tags = list(internal_tag_compiler(TAGS_NO_LINE_BREAK_AT_EOF))
        self.assertEqual(3, len(tags))
        self.assertEqual(DXFTag(10, (100, 200)), tags[1])
        self.assertEqual(DXFTag(11, (1000, 2000)), tags[2])


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


class TestStreamReader(unittest.TestCase):
    def setUp(self):
        self.reader = optimizing_stream_tagger(StringIO(TEST_TAGREADER))

    def test_next(self):
        self.assertEqual((0, 'SECTION'), next(self.reader))

    def test_to_list(self):
        tags = list(self.reader)
        self.assertEqual(8, len(tags))

    def test_no_eof(self):
        tags = list(internal_tag_compiler(TEST_NO_EOF))
        self.assertEqual(7, len(tags))
        self.assertEqual((0, 'ENDSEC'), tags[-1])

    def test_strtag_int(self):
        self.assertEqual('  1\n1\n', strtag((1, 1)))

    def test_strtag_float(self):
        self.assertEqual(' 10\n3.1415\n', strtag((10, 3.1415)))

    def test_strtag_str(self):
        self.assertEqual('  0\nSECTION\n', strtag((0, 'SECTION')))

    def test_one_point_reader(self):
        tags = list(optimizing_stream_tagger(StringIO(POINT_TAGS)))
        point_tag = tags[1]
        self.assertEqual((100, 200, 300), point_tag.value)

    def test_read_2D_points(self):
        stri = internal_tag_compiler(POINT_2D_TAGS)
        tags = list(stri)
        tag = tags[0]  # 2D point
        self.assertEqual((100, 200), tag.value)
        tag = tags[1]  # check mark
        self.assertEqual('check mark 1', tag.value)
        tag = tags[2]  # 3D point
        self.assertEqual((100, 200, 300), tag.value)
        tag = tags[3]  # check mark
        self.assertEqual('check mark 2', tag.value)

    def test_float_to_int(self):
        tags = list(internal_tag_compiler(FLOAT_FOR_INT_TAGS))
        self.assertEqual(int, type(tags[0].value))

    def test_error_tag(self):
        tags = list(optimizing_stream_tagger(StringIO(TAGS_WITH_ERROR)))
        self.assertEqual(1, len(tags))


if __name__ == '__main__':
    unittest.main()
