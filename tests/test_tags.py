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
from ezdxf.lldxf.tagger import internal_tag_compiler, skip_comments
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.tagwriter import TagWriter
from ezdxf.lldxf.types import tag_type, point_tuple
from ezdxf.lldxf.const import DXFValueError

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
        tagwriter = TagWriter(stream)
        tagwriter.write_tags(self.tags)
        result = stream.getvalue()
        stream.close()
        self.assertEqual(TEST_TAGREADER, result)

    def test_update(self):
        self.tags.update(2, 'XHEADER')
        self.assertEqual('XHEADER', self.tags[1].value)

    def test_update_error(self):
        with self.assertRaises(DXFValueError):
            self.tags.update(999, 'DOESNOTEXIST')

    def test_set_first(self):
        self.tags.set_first(999, 'NEWTAG')
        self.assertEqual('NEWTAG', self.tags[-1].value)

    def test_find_first(self):
        value = self.tags.get_first_value(9)
        self.assertEqual('$ACADVER', value)

    def test_find_first_default(self):
        value = self.tags.get_first_value(1234, default=999)
        self.assertEqual(999, value)

    def test_find_first_error(self):
        with self.assertRaises(DXFValueError):
            self.tags.get_first_value(1234)

    def test_get_handle_5(self):
        tags = Tags.from_text(TESTHANDLE5)
        self.assertEqual('F5', tags.get_handle())

    def test_get_handle_105(self):
        tags = Tags.from_text(TESTHANDLE105)
        self.assertEqual('F105', tags.get_handle())

    def test_get_handle_create_new(self):
        with self.assertRaises(DXFValueError):
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
        with self.assertRaises(DXFValueError):
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
        with self.assertRaises(DXFValueError):
            self.tags.get_handle() # handle still doesn't exist

    def test_skip_comments(self):
        tags1 = list(skip_comments(internal_tag_compiler(TEST_TAGREADER)))
        tags2 = list(skip_comments(internal_tag_compiler(TEST_TAGREADER_COMMENTS)))
        self.assertEqual(tags1, tags2)

    def test_remove_tags(self):
        self.tags.remove_tags(codes=(0, ))
        self.assertEqual(5, len(self.tags))

    def test_strip_tags(self):
        self.tags.remove_tags(codes=(0, ))
        result = Tags.strip(self.tags, codes=(0, ))
        self.assertEqual(5, len(result))
        self.assertTrue(isinstance(result, Tags))

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
