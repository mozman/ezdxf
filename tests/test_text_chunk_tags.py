# Purpose: test text2tags and vice versa
# Created: 02.05.2014
# Copyright (C) 2014, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"


import unittest
from ezdxf.lldxf.types import convert_tags_to_text_lines, convert_text_lines_to_tags, DXFTag


class TestTextChunkConverter(unittest.TestCase):
    def test_text_lines_to_tags_short_lines(self):
        text = ["123", "456", "789"]
        result = list(convert_text_lines_to_tags(text))
        self.assertEqual(result[0], (1, "123"))
        self.assertEqual(result[1], (1, "456"))
        self.assertEqual(result[2], (1, "789"))

    def test_text_lines_to_tags_long_lines(self):
        line = "0123456789" * 30
        text = [line, line]
        result = list(convert_text_lines_to_tags(text))
        self.assertEqual(4, len(result))
        self.assertEqual(result[0], (1, line[:255]))
        self.assertEqual(result[1], (3, line[255:]))
        self.assertEqual(result[2], (1, line[:255]))
        self.assertEqual(result[3], (3, line[255:]))

    def test_text_lines_to_tags_empty_list(self):
        result = list(convert_text_lines_to_tags([]))
        self.assertFalse(len(result))

    def test_tags_to_text_lines_short_lines(self):
        tags = [
            DXFTag(1, "123"),
            DXFTag(1, "456"),
            DXFTag(1, "789")
        ]
        expected = ["123", "456", "789"]
        self.assertEqual(expected, list(convert_tags_to_text_lines(tags)))

    def test_tags_to_text_lines_long_lines(self):
        line = "0123456789" * 30
        tags = [
            DXFTag(1, line[:255]),
            DXFTag(3, line[255:]),
            DXFTag(1, line[:255]),
            DXFTag(3, line[255:]),
        ]
        expected = [line, line]
        self.assertEqual(expected, list(convert_tags_to_text_lines(tags)))

    def test_tags_to_text_lines_empty_list(self):
        result = list(convert_tags_to_text_lines([]))
        self.assertFalse(len(result))
