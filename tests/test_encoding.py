#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test new binary stream char encoding/decoding
# Created: 26.03.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

import codecs
from ezdxf.lldxf.encoding import dxfbackslashreplace
codecs.register_error('dxfreplace', dxfbackslashreplace)  # setup DXF unicode encoder -> '\U+nnnn'

from ezdxf.lldxf.encoding import encode
from ezdxf.lldxf.const import DXFEncodingError

DEFAULT_ENC = 'utf-8'


class TestEncoding(unittest.TestCase):
    def test_ascii_encoding(self):
        self.assertEqual(b'123', encode(u'123', 'ascii'))

    def test_ascii_encoding_error(self):
        with self.assertRaises(DXFEncodingError):
            encode(u'123Ä', 'ascii')

    def test_ignore_ascii_encoding_error(self):
        self.assertEqual(u'123Ä'.encode(DEFAULT_ENC), encode(u'123Ä', 'ascii', ignore_error=True))

    def test_cp1252_encoding(self):
        self.assertEqual(u'123ÄÜÖ'.encode('cp1252'), encode(u'123ÄÜÖ', 'cp1252'))

    def test_cp1252_encoding_error(self):
        with self.assertRaises(DXFEncodingError):
            encode(u'更改', 'cp1252')

    def test_cp1252_ignore_encoding_error(self):
        self.assertEqual(u'更改'.encode(DEFAULT_ENC), encode(u'更改', 'cp1252', ignore_error=True))


class TestACADEncoding(unittest.TestCase):
    def test_ascii_encoding(self):
        self.assertEqual(b'123\\U+6539', u'123改'.encode('ascii', errors='dxfreplace'))


if __name__ == '__main__':
    unittest.main()
