#!/usr/bin/env python
#coding:utf-8
# Author:  mozman --<mozman@gmx.at>
# Purpose: test MText
# Created: 2013-08-11

from __future__ import unicode_literals

import unittest

import ezdxf
from ezdxf.ac1015.graphics import split_string_in_chunks, MTextBuffer
from ezdxf import const

class TestMText(unittest.TestCase):
    def setUp(self):
        self.dwg = ezdxf.new('AC1015')
        self.layout = self.dwg.modelspace()

    def test_new_short_mtext(self):
        mtext = self.layout.add_mtext("a new mtext")
        self.assertEqual("a new mtext", mtext.get_text())

    def test_new_long_mtext(self):
        text = "0123456789" * 25 + "a new mtext"
        mtext = self.layout.add_mtext(text)
        self.assertEqual(text, mtext.get_text())

    def test_new_long_mtext_2(self):
        text = "0123456789" * 25 + "abcdefghij" * 25
        mtext = self.layout.add_mtext(text)
        self.assertEqual(text, mtext.get_text())

    def test_last_text_chunk_mtext(self):
        # this tests none public details of MText class
        text = "0123456789" * 25 + "abcdefghij" * 25 + "a new mtext"
        mtext = self.layout.add_mtext(text)
        tags = mtext.tags.get_subclass("AcDbMText")
        last_text_chunk = ""
        for tag in tags:
            if tag.code == 1:
                last_text_chunk = tag.value
        self.assertEqual(last_text_chunk, "a new mtext")

    def test_get_rotation(self):
        mtext = self.layout.add_mtext('TEST')
        mtext.dxf.text_direction = (1, 1, 0) # 45 deg
        mtext.dxf.rotation = 30
        self.assertEqual(45, mtext.get_rotation())

    def test_set_rotation(self):
        mtext = self.layout.add_mtext('TEST')
        mtext.dxf.text_direction = (1, 1, 0) # 45 deg
        mtext.set_rotation(30)
        self.assertEqual(30, mtext.get_rotation())
        self.assertFalse(mtext.dxf_attrib_exists('text_direction'), msg="dxfattrib 'text_direction' should be deleted!")

    def test_buffer(self):
        text = "0123456789" * 27
        text2 = "abcdefghij" * 27
        mtext = self.layout.add_mtext(text)
        with mtext.buffer() as b:
            b.text = text2
        self.assertEqual(text2, mtext.get_text())

    def test_set_location(self):
        mtext = self.layout.add_mtext("TEST").set_location((3, 4), rotation=15, attachment_point=const.MTEXT_MIDDLE_CENTER)
        self.assertEqual(const.MTEXT_MIDDLE_CENTER, mtext.dxf.attachment_point)
        self.assertEqual(15, mtext.dxf.rotation)
        self.assertEqual((3, 4, 0), mtext.dxf.insert)


TESTSTR = "0123456789"
class TestSplitStringInChunks(unittest.TestCase):
    def test_empty_string(self):
        s = ""
        chunks = split_string_in_chunks(s, 20)
        self.assertEqual(0, len(chunks))

    def test_short_string(self):
        s = TESTSTR
        chunks = split_string_in_chunks(s, 20)
        self.assertEqual(1, len(chunks))
        self.assertEqual(TESTSTR, chunks[0])

    def test_long_string(self):
        s = TESTSTR * 3
        chunks = split_string_in_chunks(s, 20)
        self.assertEqual(2, len(chunks))
        self.assertEqual(TESTSTR*2, chunks[0])
        self.assertEqual(TESTSTR, chunks[1])

    def test_long_string_2(self):
        s = TESTSTR * 4
        chunks = split_string_in_chunks(s, 20)
        self.assertEqual(2, len(chunks))
        self.assertEqual(TESTSTR*2, chunks[0])
        self.assertEqual(TESTSTR*2, chunks[1])

class TextMTextBuffer(unittest.TestCase):
    def test_new_buffer(self):
        b = MTextBuffer("abc")
        self.assertEqual("abc", b.text)

    def test_append_text(self):
        b = MTextBuffer("abc")
        b += "def" + b.NEW_LINE

        self.assertEqual("abcdef\\P;", b.text)

if __name__ == '__main__':
    unittest.main()