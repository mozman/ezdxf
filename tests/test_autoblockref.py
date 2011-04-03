#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test autoblockref
# Created: 03.04.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
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
        blockref = self.modelspace.add_autoblockref('TEST', (0, 0), values)
        entities = list(blockref)
        self.assertEqual('INSERT', entities[0].dxftype())
        self.assertEqual('ATTRIB', entities[1].dxftype())
        self.assertEqual('TAG1', entities[1].tag)
        self.assertEqual('text1', entities[1].text)
        self.assertEqual('ATTRIB', entities[2].dxftype())
        self.assertEqual('TAG2', entities[2].tag)
        self.assertEqual('text2', entities[2].text)
        self.assertEqual('SEQEND', entities[3].dxftype())


if __name__=='__main__':
    unittest.main()