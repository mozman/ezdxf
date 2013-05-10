#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test basic graphic entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

import ezdxf


class SetupDrawing(unittest.TestCase):
    def setUp(self):
        self.dwg = ezdxf.new('AC1009')
        self.layout = self.dwg.modelspace()


class TestPaperSpace(SetupDrawing):
    def test_paper_space(self):
        paperspace = self.dwg.layout('Name it like you want, there is only one paperspace at AC1009')
        line = paperspace.add_line((0, 0), (1, 1))
        self.assertEqual(1, line.dxf.paperspace)

    def test_iter_layout(self):
        self.layout.add_line((0, 0), (1, 1))
        self.layout.add_line((0, 0), (1, 1))
        self.assertEqual(2, len(list(self.layout)))

    def test_query_entities(self):
        self.layout.add_line((0, 0), (1, 1), dxfattribs={'layer': 'lay_lines'})
        self.layout.add_line((0, 0), (1, 1), dxfattribs={'layer': 'lay_lines'})
        self.assertEqual(2, len(self.layout.query('*[layer ? "lay_.*"]')))

class TestSimpleGraphics(SetupDrawing):
    def test_create_line(self):
        line = self.layout.add_line((0, 0), (1, 1))
        self.assertEqual((0., 0.), line.dxf.start)
        self.assertEqual((1., 1.), line.dxf.end)

    def test_create_circle(self):
        circle = self.layout.add_circle((3, 3), 5)
        self.assertEqual((3., 3.), circle.dxf.center)
        self.assertEqual(5., circle.dxf.radius)

    def test_create_arc(self):
        arc = self.layout.add_arc((3, 3), 5, 30, 60)
        self.assertEqual((3., 3.), arc.dxf.center)
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

    def test_add_new_attribs_to_blockref(self):
        ref = self.layout.add_blockref('BLOCK', (0, 0))
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

if __name__ == '__main__':
    unittest.main()