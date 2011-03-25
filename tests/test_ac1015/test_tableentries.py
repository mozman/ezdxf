#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test ac1009/tableentries
# Created: 16.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from ezdxf.tags import Tags

from ezdxf.ac1015.tableentries import AC1015Layer, AC1015Linetype, AC1015Style
from ezdxf.ac1015.tableentries import AC1015AppID, AC1015BlockRecord, AC1015DimStyle
from ezdxf.ac1015.tableentries import AC1015UCS, AC1015View, AC1015Viewport

class DXFFactory:
    rootdict = { 'ACAD_PLOTSTYLENAME': 'AFAF' }

class TestNewLayer(unittest.TestCase):
    def setUp(self):
        self.layer = AC1015Layer.new('FFFF', dxffactory=DXFFactory())

    def test_get_handle(self):
        self.assertEqual('FFFF', self.layer.handle)

    def test_get_name(self):
        self.assertEqual('LayerName', self.layer.name)

    def test_default_plotstylename(self):
        handle = self.layer.tags.getvalue(390)
        self.assertEqual('AFAF', handle)

class TestNewLinetype(unittest.TestCase):
    def setUp(self):
        self.ltype = AC1015Linetype.new('FFFF', attribs={
            'name':'TEST',
            'description': 'TESTDESC',
            'pattern': [0.2, 0.1, -0.1]
        })

    def test_name(self):
        self.assertEqual('TEST', self.ltype.name)

    def test_description(self):
        self.assertEqual('TESTDESC', self.ltype.description)

    def test_pattern_items_count(self):
        def count_items():
            return len(self.ltype.tags.findall(49))
        self.assertEqual(2, self.ltype.items)
        self.assertEqual(self.ltype.items, count_items())

class TestNewStyle(unittest.TestCase):
    def setUp(self):
        self.style = AC1015Style.new('FFFF', attribs={
            'name':'TEST',
            'font': 'NOFONT.ttf',
            'width': 2.0,
        })

    def test_name(self):
        self.assertEqual('TEST', self.style.name)

class TestNewAppID(unittest.TestCase):
    def setUp(self):
        self.appid = AC1015AppID.new('FFFF', attribs={
            'name':'EZDXF',
        })

    def test_name(self):
        self.assertEqual('EZDXF', self.appid.name)

class TestNewUCS(unittest.TestCase):
    def setUp(self):
        self.ucs = AC1015UCS.new('FFFF', attribs={
            'name': 'UCS+90',
            'origin': (1.0, 1.0, 1.0),
            'xaxis': (0.0, 1.0, 0.0),
            'yaxis': (-1.0, 0.0, 0.0),
        })

    def test_name(self):
        self.assertEqual('UCS+90', self.ucs.name)

    def test_origin(self):
        self.assertEqual((1.0, 1.0, 1.0), self.ucs.origin)

class TestViewport(unittest.TestCase):
    def setUp(self):
        self.vport = AC1015Viewport.new('FFFF', attribs={
            'name':'VP1',
        })

    def test_name(self):
        self.assertEqual('VP1', self.vport.name)

class TestView(unittest.TestCase):
    def setUp(self):
        self.view = AC1015View.new('FFFF', attribs={
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
        self.assertEqual('VIEW1', self.view.name)

class TestDimstyle(unittest.TestCase):
    def setUp(self):
        self.dimstyle = AC1015DimStyle.new('FFFF', attribs={
            'name':'DIMSTYLE1',
        })

    def test_name(self):
        self.assertEqual('DIMSTYLE1', self.dimstyle.name)

    def test_handle_code(self):
        self.assertEqual('FFFF', self.dimstyle.tags.getvalue(105))

class TestBlockRecord(unittest.TestCase):
    def setUp(self):
        self.blockrec = AC1015BlockRecord.new('FFFF', attribs={
            'name':'BLOCKREC1',
        })

    def test_name(self):
        self.assertEqual('BLOCKREC1', self.blockrec.name)


if __name__=='__main__':
    unittest.main()