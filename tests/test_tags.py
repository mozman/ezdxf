# encoding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test tagreader
# Created: 10.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest
from io import StringIO

from ezdxf.tools.c23 import ustr
from ezdxf.tags import StringIterator, Tags, dxf_info
from ezdxf.dxftag import tag_type, point_tuple, strtag

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


class TestTagReader(unittest.TestCase):
    def setUp(self):
        self.reader = StringIterator(TEST_TAGREADER)

    def test_next(self):
        self.assertEqual((0, 'SECTION'), next(self.reader))

    def test_undo_last(self):
        self.reader.__next__()
        self.reader.undotag()
        self.assertEqual((0, 'SECTION'), next(self.reader))

    def test_error_on_multiple_undo_last(self):
        next(self.reader)
        self.reader.undotag()
        with self.assertRaises(ValueError):
            self.reader.undotag()

    def test_error_undo_last_before_first_read(self):
        with self.assertRaises(ValueError):
            self.reader.undotag()

    def test_lineno(self):
        next(self.reader)
        self.assertEqual(2, self.reader.lineno)

    def test_lineno_with_undo(self):
        next(self.reader)
        self.reader.undotag()
        self.assertEqual(0, self.reader.lineno)

    def test_lineno_with_undo_next(self):
        next(self.reader)
        self.reader.undotag()
        next(self.reader)
        self.assertEqual(2, self.reader.lineno)

    def test_to_list(self):
        tags = list(self.reader)
        self.assertEqual(8, len(tags))

    def test_undo_eof(self):
        for tag in self.reader:
            if tag == (0, 'EOF'):
                self.reader.undotag()
                break
        tag = next(self.reader)
        self.assertEqual((0, 'EOF'), tag)
        with self.assertRaises(StopIteration):
            self.reader.__next__()

    def test_no_eof(self):
        tags = list(StringIterator(TEST_NO_EOF))
        self.assertEqual(7, len(tags))
        self.assertEqual((0, 'ENDSEC'), tags[-1])

    def test_strtag_int(self):
        self.assertEqual('  1\n1\n', strtag((1, 1)))

    def test_strtag_float(self):
        self.assertEqual(' 10\n3.1415\n', strtag((10, 3.1415)))

    def test_strtag_str(self):
        self.assertEqual('  0\nSECTION\n', strtag((0, 'SECTION')))

    def test_one_point_reader(self):
        tags = list(StringIterator(POINT_TAGS))
        point_tag = tags[1]
        self.assertEqual((100, 200, 300), point_tag.value)

    def test_read_2D_points(self):
        stri = StringIterator(POINT_2D_TAGS)
        tags = list(stri)
        self.assertEqual(15, stri.lineno)  # 14 lines
        tag = tags[0]  # 2D point
        self.assertEqual((100, 200), tag.value)
        tag = tags[1]  # check mark
        self.assertEqual('check mark 1', tag.value)
        tag = tags[2]  # 3D point
        self.assertEqual((100, 200, 300), tag.value)
        tag = tags[3]  # check mark
        self.assertEqual('check mark 2', tag.value)

    def test_float_to_int(self):
        tags = Tags.from_text(FLOAT_FOR_INT_TAGS)
        self.assertEqual(int, type(tags[0].value))


class TestGetDXFInfo(unittest.TestCase):
    def test_dxfinfo(self):
        info = dxf_info(StringIO(TEST_TAGREADER))
        self.assertEqual(info.release, 'R2004')
        self.assertEqual(info.encoding, 'cp1252')


TESTHANDLE5 = """ 0
TEST
  5
F5
"""

TESTHANDLE105 = """ 0
TEST
105
F105
"""

TESTFINDALL = """  0
TEST0
  0
TEST1
  0
TEST2
"""


class HandlesMock:
    calls = 0

    @property
    def next(self):
        self.calls += 1
        return 'FF'


class TestTags(unittest.TestCase):
    def setUp(self):
        self.tags = Tags.from_text(TEST_TAGREADER)

    def test_from_text(self):
        self.assertEqual(8, len(self.tags))

    def test_write(self):
        stream = StringIO()
        self.tags.write(stream)
        result = stream.getvalue()
        stream.close()
        self.assertEqual(TEST_TAGREADER, result)

    def test_update(self):
        self.tags.update(2, 'XHEADER')
        self.assertEqual('XHEADER', self.tags[1].value)

    def test_update_error(self):
        with self.assertRaises(ValueError):
            self.tags.update(999, 'DOESNOTEXIST')

    def test_set_first(self):
        self.tags.set_first(999, 'NEWTAG')
        self.assertEqual('NEWTAG', self.tags[-1].value)

    def test_find_first(self):
        value = self.tags.find_first(9)
        self.assertEqual('$ACADVER', value)

    def test_find_first_default(self):
        value = self.tags.find_first(1234, default=999)
        self.assertEqual(999, value)

    def test_find_first_error(self):
        with self.assertRaises(ValueError):
            self.tags.find_first(1234)

    def test_get_handle_5(self):
        tags = Tags.from_text(TESTHANDLE5)
        self.assertEqual('F5', tags.get_handle())

    def test_get_handle_105(self):
        tags = Tags.from_text(TESTHANDLE105)
        self.assertEqual('F105', tags.get_handle())

    def test_get_handle_create_new(self):
        with self.assertRaises(ValueError):
            self.tags.get_handle()

    def test_find_all(self):
        tags = Tags.from_text(TESTFINDALL)
        self.assertEqual(3, len(tags.find_all(0)))

    def test_tag_index(self):
        tags = Tags.from_text(TESTFINDALL)
        index = tags.tag_index(0)
        self.assertEqual(0, index)
        index = tags.tag_index(0, index + 1)
        self.assertEqual(1, index)

    def test_find_first_value_error(self):
        tags = Tags.from_text(TESTFINDALL)
        with self.assertRaises(ValueError):
            tags.tag_index(1)

    def test_clone_is_equal(self):
        clone = self.tags.clone()
        self.assertTrue(self.tags is not clone)
        self.assertEqual(self.tags, clone)

    def test_clone_is_independent(self):
        clone = self.tags.clone()
        clone.pop()
        self.assertNotEqual(self.tags, clone)

    def test_replace_handle_5(self):
        tags = Tags.from_text(TESTHANDLE5)
        tags.replace_handle('AA')
        self.assertEqual('AA', tags.get_handle())

    def test_replace_handle_105(self):
        tags = Tags.from_text(TESTHANDLE105)
        tags.replace_handle('AA')
        self.assertEqual('AA', tags.get_handle())

    def test_replace_no_handle_without_error(self):
        self.tags.replace_handle('AA')
        with self.assertRaises(ValueError):
            self.tags.get_handle() # handle still doesn't exist

    def test_skip_comments(self):
        tags1 = list(StringIterator(TEST_TAGREADER))
        tags2 = list(StringIterator(TEST_TAGREADER_COMMENTS))
        self.assertEqual(tags1, tags2)

    def test_remove_tags(self):
        self.tags.remove_tags(codes=(0, ))
        self.assertEqual(5, len(self.tags))

    def test_has_tag(self):
        self.assertTrue(self.tags.has_tag(2))

    def test_has_not_tag(self):
        self.assertFalse(self.tags.has_tag(7))

DUPLICATETAGS = """  0
FIRST
  0
LAST
  1
TEST2
"""


class TestTagType(unittest.TestCase):
    def test_int(self):
        self.assertEqual(int, tag_type(60))

    def test_float(self):
        self.assertEqual(point_tuple, tag_type(10))

    def test_str(self):
        self.assertEqual(ustr, tag_type(0))

    def test_value_error(self):
        with self.assertRaises(ValueError):
            tag_type(3000)

    def test_point_tuple_2d(self):
        self.assertEqual((1, 2), point_tuple(('1', '2')))

    def test_point_tuple_3d(self):
        self.assertEqual((1, 2, 3), point_tuple(('1', '2', '3')))

COLLECT_1 = """  0
ZERO
  1
ONE
  2
TWO
  3
THREE
  4
FOUR
  0
ZERO
  1
ONE
  2
TWO
  3
THREE
  4
FOUR
"""

class TestTagsCollect(unittest.TestCase):
    def setUp(self):
        self.tags = Tags.from_text(COLLECT_1)

    def test_with_start_param(self):
        collected_tags = self.tags.collect_consecutive_tags([1, 2, 3], start=1)
        self.assertEqual(3, len(collected_tags))
        self.assertEqual("THREE", collected_tags[2].value)

    def test_with_end_param(self):
        collected_tags = self.tags.collect_consecutive_tags([0, 1, 2, 3], end=3)
        self.assertEqual(3, len(collected_tags))
        self.assertEqual("TWO", collected_tags[2].value)

    def test_with_start_and_end_param(self):
        collected_tags = self.tags.collect_consecutive_tags([1, 2, 3], start=6, end=9)
        self.assertEqual(3, len(collected_tags))
        self.assertEqual("THREE", collected_tags[2].value)

    def test_none_existing_codes(self):
        collected_tags = self.tags.collect_consecutive_tags([7, 8, 9])
        self.assertEqual(0, len(collected_tags))

    def test_all_codes(self):
        collected_tags = self.tags.collect_consecutive_tags([0, 1, 2, 3, 4])
        self.assertEqual(10, len(collected_tags))

    def test_emtpy_tags(self):
        tags = Tags()
        collected_tags = tags.collect_consecutive_tags([0, 1, 2, 3, 4])
        self.assertEqual(0, len(collected_tags))
