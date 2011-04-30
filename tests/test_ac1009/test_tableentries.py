#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test ac1009/tableentries
# Created: 16.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from ezdxf.testtools import Tags

from ezdxf.ac1009.tableentries import AC1009Layer, AC1009Linetype, AC1009Style, AC1009AppID, AC1009UCS
from ezdxf.ac1009.tableentries import AC1009View, AC1009Viewport, AC1009DimStyle

class TestNewLayer(unittest.TestCase):
    def setUp(self):
        self.layer = AC1009Layer.new('FFFF')

    def test_new_layer(self):
        self.assertEqual(6, len(self.layer.tags.noclass))

    def test_get_handle(self):
        self.assertEqual('FFFF', self.layer.dxf.handle)

    def test_get_name(self):
        self.assertEqual('LAYERNAME', self.layer.dxf.name)

    def test_get_flags(self):
        self.assertEqual(0, self.layer.dxf.flags)

    def test_get_color(self):
        self.assertEqual(7, self.layer.dxf.color)

    def test_get_linetype(self):
        self.assertEqual('CONTINUOUS', self.layer.dxf.linetype)

    def test_set_name(self):
        self.layer.dxf.name = 'MOZMAN'
        self.assertEqual('MOZMAN', self.layer.dxf.name)

    def test_set_color(self):
        self.layer.dxf.color = '1'
        self.assertEqual(1, self.layer.dxf.color)

class TestNewLinetype(unittest.TestCase):
    def setUp(self):
        self.ltype = AC1009Linetype.new('FFFF', dxfattribs={
            'name':'TEST',
            'description': 'TESTDESC',
            'pattern': [0.2, 0.1, -0.1]
        })

    def test_name(self):
        self.assertEqual('TEST', self.ltype.dxf.name)

    def test_description(self):
        self.assertEqual('TESTDESC', self.ltype.dxf.description)

    def test_pattern_items_count(self):
        def count_items():
            return len(self.ltype.tags.noclass.findall(49))
        self.assertEqual(2, self.ltype.dxf.items)
        self.assertEqual(self.ltype.dxf.items, count_items())

    def test_pattern_length(self):
        self.assertEqual(0.2, self.ltype.dxf.length)

class TestNewStyle(unittest.TestCase):
    def setUp(self):
        self.style = AC1009Style.new('FFFF', dxfattribs={
            'name':'TEST',
            'font': 'NOFONT.ttf',
            'width': 2.0,
        })

    def test_name(self):
        self.assertEqual('TEST', self.style.dxf.name)

    def test_font(self):
        self.assertEqual('NOFONT.ttf', self.style.dxf.font)

    def test_width(self):
        self.assertEqual(2.0, self.style.dxf.width)

    def test_height(self):
        self.assertEqual(0.0, self.style.dxf.height)

    def test_oblique(self):
        self.assertEqual(0.0, self.style.dxf.oblique)

    def test_bigfont(self):
        self.assertEqual('', self.style.dxf.bigfont)

class TestNewAppID(unittest.TestCase):
    def setUp(self):
        self.appid = AC1009AppID.new('FFFF', dxfattribs={
            'name':'EZDXF',
        })

    def test_name(self):
        self.assertEqual('EZDXF', self.appid.dxf.name)

class TestNewUCS(unittest.TestCase):
    def setUp(self):
        self.ucs = AC1009UCS.new('FFFF', dxfattribs={
            'name': 'UCS+90',
            'origin': (1.0, 1.0, 1.0),
            'xaxis': (0.0, 1.0, 0.0),
            'yaxis': (-1.0, 0.0, 0.0),
        })

    def test_name(self):
        self.assertEqual('UCS+90', self.ucs.dxf.name)

    def test_origin(self):
        self.assertEqual((1.0, 1.0, 1.0), self.ucs.dxf.origin)

    def test_xaxis(self):
        self.assertEqual((0.0, 1.0, 0.0), self.ucs.dxf.xaxis)

    def test_yaxis(self):
        self.assertEqual((-1.0, 0.0, 0.0), self.ucs.dxf.yaxis)

class TestViewport(unittest.TestCase):
    def setUp(self):
        self.vport = AC1009Viewport.new('FFFF', dxfattribs={
            'name':'VP1',
        })

    def test_name(self):
        self.assertEqual('VP1', self.vport.dxf.name)

class TestView(unittest.TestCase):
    def setUp(self):
        self.view = AC1009View.new('FFFF', dxfattribs={
        'name': 'VIEW1',
        'flags': 0,
        'height': 1.0,
        'width': 1.0,
        'center_point': (0, 0),
        'direction_point': (0, 0, 0),
        'target_point': (0, 0, 0),
        'lens_length': 1.0,
        'front_clipping': 0.0,
        'back_clipping': 0.0,
        'view_twist': 0.0,
        'view_mode': 0,
        })

    def test_name(self):
        self.assertEqual('VIEW1', self.view.dxf.name)

class TestDimstyle(unittest.TestCase):
    def setUp(self):
        self.dimstyle = AC1009DimStyle.new('FFFF', dxfattribs={
            'name':'DIMSTYLE1',
        })

    def test_name(self):
        self.assertEqual('DIMSTYLE1', self.dimstyle.dxf.name)

    def test_handle_code(self):
        self.assertEqual('FFFF', self.dimstyle.tags.noclass.getvalue(105))

if __name__=='__main__':
    unittest.main()