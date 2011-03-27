#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test basic graphic entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from tests.tools import DrawingProxy
from ezdxf.entityspace import EntitySpace

from ezdxf.ac1009.layouts import AC1009Layout

class SetupDrawing(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingProxy('AC1009')
        self.workspace = EntitySpace(self.dwg)
        self.layout = AC1009Layout(self.workspace, self.dwg.dxffactory, 0)

class TestPaperSpace(SetupDrawing):
    def test_paper_space(self):
        paperspace = AC1009Layout(self.workspace, self.dwg.dxffactory, 1)
        line = paperspace.add_line((0, 0), (1, 1))
        self.assertEqual(1, line.paperspace)

class TestLine(SetupDrawing):
    def test_create_line(self):
        line = self.layout.add_line((0, 0), (1, 1))
        self.assertEqual((0.,0.), line.start)
        self.assertEqual((1.,1.), line.end)

if __name__=='__main__':
    unittest.main()