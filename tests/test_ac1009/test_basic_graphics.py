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
        self.assertEqual(1, line.dxf.paperspace)

class TestSimpleGraphics(SetupDrawing):
    def test_create_line(self):
        line = self.layout.add_line((0, 0), (1, 1))
        self.assertEqual((0.,0.), line.dxf.start)
        self.assertEqual((1.,1.), line.dxf.end)

    def test_create_circle(self):
        circle = self.layout.add_circle((3, 3), 5)
        self.assertEqual((3.,3.), circle.dxf.center)
        self.assertEqual(5., circle.dxf.radius)

    def test_create_arc(self):
        arc = self.layout.add_arc((3, 3), 5, 30, 60)
        self.assertEqual((3.,3.), arc.dxf.center)
        self.assertEqual(5., arc.dxf.radius)
        self.assertEqual(30., arc.dxf.startangle)
        self.assertEqual(60., arc.dxf.endangle)

    def test_create_trace(self):
        trace = self.layout.add_trace([(0, 0), (1, 0), (1, 1), (0, 1)])
        self.assertEqual((0, 0), trace[0])
        self.assertEqual((1, 0), trace.dxf.vtx1)
        self.assertEqual((1, 1), trace[2])
        self.assertEqual((0, 1), trace.dxf.vtx3)

    def test_create_solid(self):
        trace = self.layout.add_solid([(0, 0), (1, 0), (1, 1)])
        self.assertEqual((0, 0), trace.dxf.vtx0)
        self.assertEqual((1, 0), trace[1])
        self.assertEqual((1, 1), trace.dxf.vtx2)
        self.assertEqual((1, 1), trace[3])

    def test_create_3dface(self):
        trace = self.layout.add_3Dface([(0, 0), (1, 0), (1, 1), (0, 1)])
        self.assertEqual((0, 0), trace.dxf.vtx0)
        self.assertEqual((1, 0), trace[1])
        self.assertEqual((1, 1), trace.dxf.vtx2)
        self.assertEqual((0, 1), trace[3])

class TestText(SetupDrawing):
    def test_create_text(self):
        text = self.layout.add_text('text')
        self.assertEqual('text', text.dxf.text)

class TestBlock(SetupDrawing):
    def test_create_blockref(self):
        ref = self.layout.add_blockref('BLOCK', (0, 0))
        self.assertEqual('BLOCK', ref.dxf.name)
        self.assertEqual((0., 0.), ref.dxf.insert)
        self.assertEqual(0, ref.dxf.attribsfollow)

    def test_add_new_attribs_to_blockref(self):
        ref = self.layout.add_blockref('BLOCK', (0, 0))
        self.assertEqual(0, ref.dxf.attribsfollow)
        ref.add_attrib('TEST', 'text', (0, 0))
        self.assertEqual(1, ref.dxf.attribsfollow)
        attrib = ref.get_attrib('TEST')
        self.assertEqual('text', attrib.dxf.text)

    def test_add_to_attribs_to_blockref(self):
        ref = self.layout.add_blockref('BLOCK', (0, 0))
        ref.add_attrib('TEST1', 'text1', (0, 0))
        ref.add_attrib('TEST2', 'text2', (0, 0))
        attribs = [attrib.dxf.tag for attrib in ref]
        self.assertEqual(['TEST1', 'TEST2'], attribs)

    def test_has_seqend(self):
        ref = self.layout.add_blockref('BLOCK', (0, 0))
        ref.add_attrib('TEST1', 'text1', (0, 0))
        ref.add_attrib('TEST2', 'text2', (0, 0))
        entity = self.layout._get_entity_at_index(-1)
        self.assertEqual('SEQEND', entity.dxftype())

if __name__=='__main__':
    unittest.main()