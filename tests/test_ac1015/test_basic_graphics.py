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

DWG_AC1015 = ezdxf.new('AC1015')
DWG_AC1018 = ezdxf.new('AC1018')
DWG_AC1021 = ezdxf.new('AC1021')


class SetupDrawing(unittest.TestCase):
    def setUp(self):
        self.layout = DWG_AC1015.modelspace()


class TestAC1015GraphicsDefaultSettings(SetupDrawing):
    def test_default_settings(self):
        line = self.layout.add_line((0, 0), (1, 1))
        self.assertEqual('0', line.dxf.layer)
        self.assertEqual(256, line.dxf.color)
        self.assertEqual('BYLAYER', line.dxf.linetype)
        self.assertEqual(1.0, line.dxf.ltscale)
        self.assertEqual(0, line.dxf.invisible)
        self.assertEqual((0.0, 0.0, 1.0), line.dxf.extrusion)
        with self.assertRaises(ValueError):  # requires AC1018
            value = line.dxf.true_color
        with self.assertRaises(ValueError):  # requires AC1018
            value = line.dxf.color_name
        with self.assertRaises(ValueError):  # requires AC1018
            value = line.dxf.transparency
        with self.assertRaises(ValueError):  # requires AC1021
            value = line.dxf.shadow_mode
        with self.assertRaises(ValueError):  # not defined value
            value = line.dxf.lineweight

        line.dxf.lineweight = 17  # set line weight
        self.assertEqual(17, line.dxf.lineweight)  # get line weight


class TestAC1018GraphicsDefaultSettings(unittest.TestCase):
    def setUp(self):
        self.layout = DWG_AC1018.modelspace()

    def test_default_settings(self):
        line = self.layout.add_line((0, 0), (1, 1))
        self.assertFalse(line.dxf_attrib_exists('true_color'))  # no default true color
        self.assertFalse(line.dxf_attrib_exists('color_name'))  # no default color name
        self.assertFalse(line.dxf_attrib_exists('transparency'))  # no default transparency
        with self.assertRaises(ValueError):  # requires AC1021
            value = line.dxf.shadow_mode

    def test_true_color(self):
        line = self.layout.add_line((0, 0), (1, 1))
        line.dxf.true_color = 0x0F0F0F
        self.assertEqual(0x0F0F0F, line.dxf.true_color)
        self.assertEqual((0x0F, 0x0F, 0x0F), line.rgb)  # shortcut for modern graphic entities
        line.rgb = (255, 255, 255)  # shortcut for modern graphic entities
        self.assertEqual(0xFFFFFF, line.dxf.true_color)

    def test_color_name(self):
        line = self.layout.add_line((0, 0), (1, 1))
        line.dxf.color_name = "Rot"
        self.assertEqual("Rot", line.dxf.color_name)

    def test_transparency(self):
        line = self.layout.add_line((0, 0), (1, 1))
        line.dxf.transparency = 0x020000FF  # 0xFF = opaque; 0x00 = 100% transparent
        self.assertEqual(0x020000FF, line.dxf.transparency)
        # recommend usage: helper property ModernGraphicEntity.transparency
        self.assertEqual(0., line.transparency)  # 0. =  opaque; 1. = 100% transparent
        line.transparency = 1.0
        self.assertEqual(0x02000000, line.dxf.transparency)


class TestAC1021GraphicsDefaultSettings(unittest.TestCase):
    def setUp(self):
        self.layout = DWG_AC1018.modelspace()

    def test_default_settings(self):
        line = self.layout.add_line((0, 0), (1, 1))
        self.assertFalse(line.dxf_attrib_exists('shadow_mode'))  # no default shadow_mode


class TestBasicEntities(SetupDrawing):
    def test_iter_layout(self):
        entity_count = len(list(self.layout))
        self.layout.add_line((0, 0), (1, 1))
        self.layout.add_line((0, 0), (1, 1))
        self.assertEqual(entity_count+2, len(list(self.layout)))

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
        trace = self.layout.add_3dface([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)])
        self.assertEqual((0, 0, 0), trace.dxf.vtx0)
        self.assertEqual((1, 0, 0), trace[1])
        self.assertEqual((1, 1, 0), trace.dxf.vtx2)
        self.assertEqual((0, 1, 0), trace[3])

    def test_create_text(self):
        text = self.layout.add_text('text')
        self.assertEqual('text', text.dxf.text)


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

    def test_get_pos_TOP_CENTER(self):
        text = self.layout.add_text('text')
        text.set_pos((2, 2), align="TOP_CENTER")
        align, p1, p2 = text.get_pos()
        self.assertEqual("TOP_CENTER", align)
        self.assertEqual(p1, (2, 2))
        self.assertIsNone(p2)

    def test_get_pos_LEFT(self):
        text = self.layout.add_text('text')
        text.set_pos((2, 2))
        align, p1, p2 = text.get_pos()
        self.assertEqual("LEFT", align)
        self.assertEqual(p1, (2, 2))
        self.assertIsNone(p2)


class TestShape(SetupDrawing):
    def test_create_shape(self):
        shape = self.layout.add_shape("TestShape", (1, 2), 3.0)
        self.assertEqual("TestShape", shape.dxf.name)
        self.assertEqual((1.0, 2.0), shape.dxf.insert)
        self.assertEqual(3.0, shape.dxf.size)
        self.assertEqual(0.0, shape.dxf.rotation)
        self.assertEqual(1.0, shape.dxf.xscale)
        self.assertEqual(0.0, shape.dxf.oblique)


class TestRay(SetupDrawing):
    def test_create_ray(self):
        ray = self.layout.add_ray((1, 2, 0), (1, 0, 0))
        self.assertEqual((1, 2, 0), ray.dxf.start)
        self.assertEqual((1, 0, 0), ray.dxf.unit_vector)


class TestXLine(SetupDrawing):
    def test_create_ray(self):
        xline = self.layout.add_xline((1, 2, 0), (1, 0, 0))
        self.assertEqual((1, 2, 0), xline.dxf.start)
        self.assertEqual((1, 0, 0), xline.dxf.unit_vector)


if __name__ == '__main__':
    unittest.main()