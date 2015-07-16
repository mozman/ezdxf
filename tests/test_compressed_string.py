# encoding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test compressed strings
# Created: 30.04.2014
# Copyright (C) 2014, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

from ezdxf.tools.compressedstring import CompressedString


class TestCompressedString(unittest.TestCase):
    def test_init(self):
        self.assertEqual('compressed data', str(CompressedString("")))

    def test_decompress(self):
        cs = CompressedString('test')
        self.assertEqual('compressed data', str(cs))
        self.assertEqual('test', cs.decompress())

    def test_compress_big_string(self):
        s = "123456789" * 1000
        cs = CompressedString(s)
        self.assertEqual(s, cs.decompress())
        self.assertTrue(len(s) > len(cs))

    def test_return_type(self):
        s = "123456789" * 10
        result = CompressedString(s).decompress()
        self.assertEqual(type(s), type(result))

    def test_non_ascii_chars(self):
        s = "12345äöüß6789" * 10
        result = CompressedString(s).decompress()
        self.assertEqual(s, result)
        self.assertEqual(type(s), type(result))


if __name__ == '__main__':
    unittest.main()
