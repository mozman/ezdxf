#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test blocks
# Created: 02.04.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from ezdxf.testtools import DrawingProxy, Tags

from ezdxf.blockssection import BlocksSection

class TestBlocksSection(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingProxy('AC1009')
        self.blocks = BlocksSection(Tags.fromtext(EMPTYSEC), self.dwg)

    def test_create_block(self):
        block = self.blocks.new('TEST')
        self.assertTrue(block in self.blocks)

EMPTYSEC = """  0
SECTION
  2
BLOCKS
  0
ENDSEC
"""

if __name__=='__main__':
    unittest.main()