#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test autoblockref
# Created: 03.04.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals

import unittest

import ezdxf


class TestAutoBlockref(unittest.TestCase):
    def setUp(self):
        self.dwg = ezdxf.new()
        self.modelspace = self.dwg.modelspace()
        self.block = self.dwg.blocks.new('TEST')
        self.block.add_attdef('TAG1', (0, 0))
        self.block.add_attdef('TAG2', (0, 5))

    def test_create_auto_attribs(self):
        values = {'TAG1': 'text1', 'TAG2': 'text2'}
        blockref = self.modelspace.add_auto_blockref('TEST', (0, 0), values)
        autoblock = self.dwg.blocks[blockref.dxf.name]
        entities = list(autoblock)
        insert = entities[0]
        self.assertEqual('INSERT', insert.dxftype())
        attribs = list(insert.attribs())
        attrib1, attrib2 = attribs
        self.assertEqual('ATTRIB', attrib1.dxftype())
        self.assertEqual('TAG1', attrib1.dxf.tag)
        self.assertEqual('text1', attrib1.dxf.text)
        self.assertEqual('ATTRIB', attrib2.dxftype())
        self.assertEqual('TAG2', attrib2.dxf.tag)
        self.assertEqual('text2', attrib2.dxf.text)

    def test_has_attdef(self):
        self.assertTrue(self.block.has_attdef('TAG1'))
        self.assertFalse(self.block.has_attdef('TAG_Z'))

    def test_get_attdef(self):
        attdef = self.block.get_attdef('TAG1')
        self.assertEqual(attdef.dxf.tag, 'TAG1')
        attdef = self.block.get_attdef('TAG1_Z')
        self.assertIsNone(attdef)

    def test_get_attdef_text(self):
        self.block.add_attdef('TAGX', (0, 0), text='PRESET_TEXT')
        text = self.block.get_attdef_text('TAGX')
        self.assertEqual(text, 'PRESET_TEXT')

    def test_attdef_getter_properties(self):
        attrib = self.block.get_attdef('TAG1')

        self.assertFalse(attrib.is_const)
        self.assertFalse(attrib.is_invisible)
        self.assertFalse(attrib.is_verify)
        self.assertFalse(attrib.is_preset)

    def test_attdef_setter_properties(self):
        attrib = self.block.get_attdef('TAG1')

        self.assertFalse(attrib.is_const)
        attrib.is_const = True
        self.assertTrue(attrib.is_const)

        self.assertFalse(attrib.is_invisible)
        attrib.is_invisible = True
        self.assertTrue(attrib.is_invisible)

        self.assertFalse(attrib.is_verify)
        attrib.is_verify = True
        self.assertTrue(attrib.is_verify)

        self.assertFalse(attrib.is_preset)
        attrib.is_preset = True
        self.assertTrue(attrib.is_preset)


if __name__ == '__main__':
    unittest.main()