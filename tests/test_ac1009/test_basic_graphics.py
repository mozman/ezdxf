#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test basic graphic entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from ezdxf.testtools import DrawingProxy
from ezdxf.entityspace import EntitySpace

from ezdxf.ac1009.layouts import AC1009Layout

class SetupDrawing(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingProxy('AC1009')
        self.entityspace = EntitySpace(self.dwg.entitydb)
        self.layout = AC1009Layout(self.entityspace, self.dwg.dxffactory, 0)

class TestPaperSpace(SetupDrawing):
    def test_paper_space(self):
        paperspace = AC1009Layout(self.entityspace, self.dwg.dxffactory, 1)
        line = paperspace.add_line((0, 0), (1, 1))
        self.assertEqual(1, line.paperspace)

class TestSimpleGraphics(SetupDrawing):
    def test_create_line(self):
        line = self.layout.add_line((0, 0), (1, 1))
        self.assertEqual((0.,0.), line.start)
        self.assertEqual((1.,1.), line.end)

    def test_create_circle(self):
        circle = self.layout.add_circle((3, 3), 5)
        self.assertEqual((3.,3.), circle.center)
        self.assertEqual(5., circle.radius)

    def test_create_arc(self):
        arc = self.layout.add_arc((3, 3), 5, 30, 60)
        self.assertEqual((3.,3.), arc.center)
        self.assertEqual(5., arc.radius)
        self.assertEqual(30., arc.startangle)
        self.assertEqual(60., arc.endangle)

    def test_create_trace(self):
        trace = self.layout.add_trace([(0, 0), (1, 0), (1, 1), (0, 1)])
        self.assertEqual((0, 0), trace[0])
        self.assertEqual((1, 0), trace.vtx1)
        self.assertEqual((1, 1), trace[2])
        self.assertEqual((0, 1), trace.vtx3)

    def test_create_solid(self):
        trace = self.layout.add_solid([(0, 0), (1, 0), (1, 1)])
        self.assertEqual((0, 0), trace.vtx0)
        self.assertEqual((1, 0), trace[1])
        self.assertEqual((1, 1), trace.vtx2)
        self.assertEqual((1, 1), trace[3])

    def test_create_3dface(self):
        trace = self.layout.add_3Dface([(0, 0), (1, 0), (1, 1), (0, 1)])
        self.assertEqual((0, 0), trace.vtx0)
        self.assertEqual((1, 0), trace[1])
        self.assertEqual((1, 1), trace.vtx2)
        self.assertEqual((0, 1), trace[3])

class TestText(SetupDrawing):
    def test_create_text(self):
        text = self.layout.add_text('text')
        self.assertEqual('text', text.text)

class TestBlock(SetupDrawing):
    def test_create_blockref(self):
        ref = self.layout.add_blockref('BLOCK', (0, 0))
        self.assertEqual('BLOCK', ref.name)
        self.assertEqual((0., 0.), ref.insert)

if __name__=='__main__':
    unittest.main()