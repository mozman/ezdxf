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

from ezdxf.ac1015.tableentries import Layer, Linetype, Style
from ezdxf.ac1015.tableentries import AppID, BlockRecord, DimStyle
from ezdxf.ac1015.tableentries import UCS, View, Viewport

class DXFFactory:
    rootdict = { 'ACAD_PLOTSTYLENAME': 'AFAF' }

class TestNewLayer(unittest.TestCase):
    def setUp(self):
        self.layer = Layer.new('FFFF', dxffactory=DXFFactory())

    def test_get_handle(self):
        self.assertEqual('FFFF', self.layer.dxf.handle)

    def test_get_name(self):
        self.assertEqual('LayerName', self.layer.dxf.name)

    def test_default_plotstylename(self):
        self.assertEqual('AFAF', self.layer.dxf.plotstylename)

class TestNewLinetype(unittest.TestCase):
    def setUp(self):
        self.ltype = Linetype.new('FFFF', dxfattribs={
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
            subclass = self.ltype.tags.get_subclass('AcDbLinetypeTableRecord')
            return len(subclass.findall(49))
        self.assertEqual(2, self.ltype.dxf.items)
        self.assertEqual(self.ltype.dxf.items, count_items())

class TestNewStyle(unittest.TestCase):
    def setUp(self):
        self.style = Style.new('FFFF', dxfattribs={
            'name':'TEST',
            'font': 'NOFONT.ttf',
            'width': 2.0,
        })

    def test_name(self):
        self.assertEqual('TEST', self.style.dxf.name)

class TestNewAppID(unittest.TestCase):
    def setUp(self):
        self.appid = AppID.new('FFFF', dxfattribs={
            'name':'EZDXF',
        })

    def test_name(self):
        self.assertEqual('EZDXF', self.appid.dxf.name)

class TestNewUCS(unittest.TestCase):
    def setUp(self):
        self.ucs = UCS.new('FFFF', dxfattribs={
            'name': 'UCS+90',
            'origin': (1.0, 1.0, 1.0),
            'xaxis': (0.0, 1.0, 0.0),
            'yaxis': (-1.0, 0.0, 0.0),
        })

    def test_name(self):
        self.assertEqual('UCS+90', self.ucs.dxf.name)

    def test_origin(self):
        self.assertEqual((1.0, 1.0, 1.0), self.ucs.dxf.origin)

class TestViewport(unittest.TestCase):
    def setUp(self):
        self.vport = Viewport.new('FFFF', dxfattribs={
            'name':'VP1',
        })

    def test_name(self):
        self.assertEqual('VP1', self.vport.dxf.name)

class TestView(unittest.TestCase):
    def setUp(self):
        self.view = View.new('FFFF', dxfattribs={
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
        self.dimstyle = DimStyle.new('FFFF', dxfattribs={
            'name':'DIMSTYLE1',
        })

    def test_name(self):
        self.assertEqual('DIMSTYLE1', self.dimstyle.dxf.name)

    def test_handle_code(self):
        handle = self.dimstyle.tags.noclass.getvalue(105)
        self.assertEqual('FFFF', handle)

class TestBlockRecord(unittest.TestCase):
    def setUp(self):
        self.blockrec = BlockRecord.new('FFFF', dxfattribs={
            'name':'BLOCKREC1',
        })

    def test_name(self):
        self.assertEqual('BLOCKREC1', self.blockrec.dxf.name)


if __name__=='__main__':
    unittest.main()