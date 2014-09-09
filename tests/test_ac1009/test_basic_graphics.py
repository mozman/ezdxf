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

DWG = ezdxf.new('AC1009')


def new_drawing():
    dwg = ezdxf.new('AC1009')
    msp = dwg.modelspace()
    return dwg, msp


class SetupDrawing(unittest.TestCase):
    def setUp(self):
        self.layout = DWG.modelspace()


class TestModelSpace(SetupDrawing):
    def test_drawing_attribute(self):
        line = self.layout.add_line((0, 0), (1, 1))
        self.assertEqual(DWG, line.drawing)

    def test_dxffactory_property(self):
        line = self.layout.add_line((0, 0), (1, 1))
        self.assertEqual(DWG.dxffactory, line.dxffactory)

    def test_delete_entity(self):
        dwg, layout = new_drawing()
        for _ in range(5):
            layout.add_line((0, 0), (10, 0))
        lines = layout.query('LINE')
        self.assertEqual(5, len(lines))
        line3 = lines[2]
        layout.delete_entity(line3)
        self.assertTrue(line3.dxf.paperspace < 0, "Paper space attribute has to be invalid (<0).")
        self.assertFalse(line3 in layout)
        self.assertFalse(line3.dxf.handle in dwg.entitydb)

    def test_delete_polyline(self):
        entity_count = len(list(self.layout))
        pline = self.layout.add_polyline3d([(0, 0, 0), (1, 2, 3), (4, 5, 6)])
        self.assertEqual(entity_count+1, len(list(self.layout)))  # 1x POLYLINE rest is linked to the POLYLINE entity
        self.layout.delete_entity(pline)
        self.assertEqual(entity_count, len(list(self.layout)))

    def test_delete_blockref_with_attribs(self):
        entity_count = len(list(self.layout))
        blockref = self.layout.add_blockref("TESTBLOCK", (0, 0))
        blockref.add_attrib('TAG1', "Text1", (0, 1))
        blockref.add_attrib('TAG2', "Text2", (0, 2))
        blockref.add_attrib('TAG3', "Text3", (0, 3))
        self.assertEqual(entity_count+1, len(list(self.layout)))  # 1x INSERT, rest is linked to the INSERT entity
        self.layout.delete_entity(blockref)
        self.assertEqual(entity_count, len(list(self.layout)))

    def test_delete_all_entities(self):
        paper_space = DWG.layout()
        paper_space_count = len(paper_space)
        model_space = DWG.modelspace()
        model_space_count = len(model_space)
        for _ in range(5):
            model_space.add_line((0, 0), (1, 1))
            paper_space.add_line((0, 0), (1, 1))

        self.assertEqual(model_space_count + 5, len(model_space))
        self.assertEqual(paper_space_count + 5, len(paper_space))

        model_space.delete_all_entities()
        self.assertEqual(0, len(model_space))
        self.assertEqual(paper_space_count + 5, len(paper_space))


class TestPaperSpace(SetupDrawing):
    def test_paper_space(self):
        paperspace = DWG.layout('Name it like you want, there is only one paperspace at AC1009')
        line = paperspace.add_line((0, 0), (1, 1))
        self.assertEqual(1, line.dxf.paperspace)

    def test_iter_layout(self):
        paper_space = DWG.layout()
        paper_space.delete_all_entities()
        paper_space.add_line((0, 0), (1, 1))
        paper_space.add_line((0, 0), (1, 1))
        entities = list(paper_space)
        self.assertEqual(2, len(entities))
        # Are all necessary attribute set?
        e = entities[0]
        self.assertEqual(DWG, e.drawing)

    def test_query_entities(self):
        paper_space = DWG.layout()
        paper_space.delete_all_entities()
        paper_space.add_line((0, 0), (1, 1), dxfattribs={'layer': 'lay_lines'})
        paper_space.add_line((0, 0), (1, 1), dxfattribs={'layer': 'lay_lines'})
        entities = paper_space.query('*[layer ? "lay_.*"]')
        self.assertEqual(2, len(entities))
        # Are all necessary attribute set?
        e = entities[0]
        self.assertEqual(DWG, e.drawing)

    def test_model_space_get_layout_for_entity(self):
        model_space = DWG.modelspace()
        line = model_space.add_line((0, 0), (1, 1))
        layout = DWG.layouts.get_layout_for_entity(line)
        self.assertEqual(model_space, layout)

    def test_paper_space_get_layout_for_entity(self):
        paper_space = DWG.layout()
        line = paper_space.add_line((0, 0), (1, 1))
        layout = DWG.layouts.get_layout_for_entity(line)
        self.assertEqual(paper_space, layout)


class TestGraphicsDefaultSettings(SetupDrawing):
    def test_default_settings(self):
        line = self.layout.add_line((0, 0), (1, 1))
        self.assertEqual('0', line.dxf.layer)
        self.assertEqual(256, line.dxf.color)
        self.assertEqual('BYLAYER', line.dxf.linetype)
        self.assertEqual((0.0, 0.0, 1.0), line.dxf.extrusion)


class TestDXFEntity(SetupDrawing):
    def test_clone_dxf_attribs(self):
        line = self.layout.add_line((0, 0), (1, 1))
        attribs = line.clone_dxf_attribs()
        self.assertFalse('extrusion' in attribs, "Don't clone unset attribs with default values.")

    def test_dxf_attrib_exists(self):
        line = self.layout.add_line((0, 0), (1, 1))
        self.assertFalse(line.dxf_attrib_exists('extrusion'), "Ignore unset attribs with default values.")


class TestSimpleGraphics(SetupDrawing):
    def test_clone_dxf_attribs(self):
        line = self.layout.add_line((0, 0), (1, 1))
        attribs = line.clone_dxf_attribs()
        self.assertFalse('extrusion' in attribs, "Don't clone unset attribs with default values.")

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
        trace = self.layout.add_3Dface([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)])
        self.assertEqual((0, 0, 0), trace.dxf.vtx0)
        self.assertEqual((1, 0, 0), trace[1])
        self.assertEqual((1, 1, 0), trace.dxf.vtx2)
        self.assertEqual((0, 1, 0), trace[3])


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

    def test_get_pos(self):
        text = self.layout.add_text('text')
        text.set_pos((2, 2), align="TOP_CENTER")
        align, p1, p2 = text.get_pos()
        self.assertEqual("TOP_CENTER", align)
        self.assertEqual(p1, (2, 2))
        self.assertIsNone(p2)


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
        attribs = [attrib.dxf.tag for attrib in ref.attribs()]
        self.assertEqual(['TEST1', 'TEST2'], attribs)

    def test_has_seqend(self):
        ref = self.layout.add_blockref('BLOCK', (0, 0))
        ref.add_attrib('TEST1', 'text1', (0, 0))
        ref.add_attrib('TEST2', 'text2', (0, 0))
        entity = ref.get_attrib('TEST2')
        seqend = self.layout.entitydb[entity.tags.link]
        self.assertEqual('SEQEND', seqend.dxftype())

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


class TestShape(SetupDrawing):
    def test_create_shape(self):
        shape = self.layout.add_shape("TestShape", (1, 2), 3.0)
        self.assertEqual("TestShape", shape.dxf.name)
        self.assertEqual((1.0, 2.0), shape.dxf.insert)
        self.assertEqual(3.0, shape.dxf.size)
        self.assertEqual(0.0, shape.dxf.rotation)
        self.assertEqual(1.0, shape.dxf.xscale)
        self.assertEqual(0.0, shape.dxf.oblique)

if __name__ == '__main__':
    unittest.main()