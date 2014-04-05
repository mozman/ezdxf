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


class TestGraphicsEntity(SetupDrawing):
    def test_layout_property(self):
        line = self.layout.add_line((0, 0), (1, 1))
        self.assertEqual(self.layout, line.layout)

    def test_drawing_attribute(self):
        line = self.layout.add_line((0, 0), (1, 1))
        self.assertEqual(self.dwg, line.drawing)

    def test_dxffactory_property(self):
        line = self.layout.add_line((0, 0), (1, 1))
        self.assertEqual(self.dwg.dxffactory, line.dxffactory)

    def test_layout_attribute(self):
        line = self.layout.add_line((0, 0), (1, 1))
        self.assertEqual(self.layout, line.layout)


class TestPaperSpace(SetupDrawing):
    def test_paper_space(self):
        paperspace = self.dwg.layout('Name it like you want, there is only one paperspace at AC1009')
        line = paperspace.add_line((0, 0), (1, 1))
        self.assertEqual(1, line.dxf.paperspace)
        self.assertEqual(paperspace, line.layout)

    def test_iter_layout(self):
        self.layout.add_line((0, 0), (1, 1))
        self.layout.add_line((0, 0), (1, 1))
        entities = list(self.layout)
        self.assertEqual(2, len(entities))
        # Are all necessary attribute set?
        e = entities[0]
        self.assertEqual(self.dwg, e.drawing)
        self.assertEqual(self.layout, e.layout)

    def test_query_entities(self):
        self.layout.add_line((0, 0), (1, 1), dxfattribs={'layer': 'lay_lines'})
        self.layout.add_line((0, 0), (1, 1), dxfattribs={'layer': 'lay_lines'})
        entities = self.layout.query('*[layer ? "lay_.*"]')
        self.assertEqual(2, len(entities))
        # Are all necessary attribute set?
        e = entities[0]
        self.assertEqual(self.dwg, e.drawing)
        self.assertEqual(self.layout, e.layout)

    def test_model_space_get_layout_for_entity(self):
        line = self.layout.add_line((0, 0), (1, 1))
        layout = self.dwg.layouts.get_layout_for_entity(line)
        self.assertEqual(self.layout, layout)

    def test_paper_space_get_layout_for_entity(self):
        paper_space = self.dwg.layout()
        line = paper_space.add_line((0, 0), (1, 1))
        layout = self.dwg.layouts.get_layout_for_entity(line)
        self.assertEqual(paper_space, layout)


class TestSimpleGraphics(SetupDrawing):
    def test_create_line(self):
        line = self.layout.add_line((0, 0), (1, 1))
        self.assertEqual((0., 0.), line.dxf.start)
        self.assertEqual((1., 1.), line.dxf.end)

    def test_create_point(self):
        line = self.layout.add_point((1, 2))
        self.assertEqual((1, 2), line.dxf.location)

    def test_create_circle(self):
        circle = self.layout.add_circle((3, 3), 5)
        self.assertEqual((3., 3.), circle.dxf.center)
        self.assertEqual(5., circle.dxf.radius)

    def test_create_arc(self):
        arc = self.layout.add_arc((3, 3), 5, 30, 60)
        self.assertEqual((3., 3.), arc.dxf.center)
        self.assertEqual(5., arc.dxf.radius)
        self.assertEqual(30., arc.dxf.start_angle)
        self.assertEqual(60., arc.dxf.end_angle)

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

    def test_set_alignment(self):
        text = self.layout.add_text('text')
        text.set_pos((2, 2), align="TOP_CENTER")
        self.assertEqual(1, text.dxf.halign)
        self.assertEqual(3, text.dxf.valign)
        self.assertEqual((2, 2), text.dxf.align_point)

    def test_set_fit_alignment(self):
        text = self.layout.add_text('text')
        text.set_pos((2, 2), (4, 2), align="FIT")
        self.assertEqual(5, text.dxf.halign)
        self.assertEqual(0, text.dxf.valign)
        self.assertEqual((2, 2), text.dxf.insert)
        self.assertEqual((4, 2), text.dxf.align_point)

    def test_get_alignment(self):
        text = self.layout.add_text('text')
        text.dxf.halign = 1
        text.dxf.valign = 3
        self.assertEqual('TOP_CENTER', text.get_align())


class TestBlock(SetupDrawing):
    def test_create_blockref(self):
        ref = self.layout.add_blockref('BLOCK', (0, 0))
        self.assertEqual('BLOCK', ref.dxf.name)
        self.assertEqual((0., 0.), ref.dxf.insert)

    def test_add_new_attribs_to_blockref(self):
        ref = self.layout.add_blockref('BLOCK', (0, 0))
        ref.add_attrib('TEST', 'text', (0, 0))
        self.assertEqual(1, ref.dxf.attribs_follow)
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
        entity = self.layout.get_entity_at_index(-1)
        self.assertEqual('SEQEND', entity.dxftype())

    def test_insert_place(self):
        ref = self.layout.add_blockref('BLOCK', (0, 0))
        ref.place(insert=(1, 2), scale=(0.5, 0.4, 0.3), rotation=37.0)
        self.assertEqual((1, 2), ref.dxf.insert)
        self.assertEqual(0.5, ref.dxf.xscale)
        self.assertEqual(0.4, ref.dxf.yscale)
        self.assertEqual(0.3, ref.dxf.zscale)
        self.assertEqual(37.0, ref.dxf.rotation)

    def test_insert_grid(self):
        ref = self.layout.add_blockref('BLOCK', (0, 0))
        ref.grid(size=(2, 3), spacing=(5, 10))
        self.assertEqual(2, ref.dxf.row_count)
        self.assertEqual(3, ref.dxf.column_count)
        self.assertEqual(5, ref.dxf.row_spacing)
        self.assertEqual(10, ref.dxf.column_spacing)

if __name__ == '__main__':
    unittest.main()