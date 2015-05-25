#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test hatch entity
# Created: 25.05.2015
# Copyright (C) 2015, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

from ezdxf.modern.hatch import Hatch, _HATCH_TPL
from ezdxf.classifiedtags import ClassifiedTags, DXFTag

class TestHatch(unittest.TestCase):
    def setUp(self):
        tags = ClassifiedTags.from_text(_HATCH_TPL)
        self.hatch = Hatch(tags)

    def test_default_settings(self):
        hatch = self.hatch
        self.assertEqual('0', hatch.dxf.layer)
        self.assertEqual(1, hatch.dxf.color)
        self.assertEqual('BYLAYER', hatch.dxf.linetype)
        self.assertEqual(1.0, hatch.dxf.ltscale)
        self.assertEqual(0, hatch.dxf.invisible)
        self.assertEqual((0.0, 0.0, 1.0), hatch.dxf.extrusion)
        self.assertEqual((0.0, 0.0, 0.0), hatch.dxf.elevation)

    def test_default_hatch_settings(self):
        hatch = self.hatch
        self.assertEqual(1, hatch.dxf.solid_fill)
        self.assertEqual(1, hatch.dxf.hatch_style)
        self.assertEqual(1, hatch.dxf.pattern_type)
        self.assertEqual(0.0, hatch.dxf.pattern_angle)
        self.assertEqual(1.0, hatch.dxf.pattern_scale)
        self.assertEqual(0, hatch.dxf.pattern_double)
        self.assertEqual(1, hatch.dxf.n_seed_points)

    def test_get_seed_points(self):
        hatch = self.hatch
        seed_points = hatch.get_seed_points()
        self.assertEqual(1, len(seed_points))
        self.assertEqual((0., 0.), seed_points[0])

    def test_set_seed_points(self):
        hatch = self.hatch
        seed_points = [(1.0, 1.0), (2.0, 2.0)]
        hatch.set_seed_points(seed_points)
        self.assertEqual(2, hatch.dxf.n_seed_points)
        new_seed_points = hatch.get_seed_points()
        self.assertEqual(seed_points, new_seed_points)
        # low level test
        tags = hatch.AcDbHatch
        index = tags.tag_index(98)  # pos of 'Number of seed points'
        self.assertEqual((1.0, 1.0), tags[index+1].value)
        self.assertEqual((2.0, 2.0), tags[index+2].value)

    def test_set_seed_points_low_level(self):
        tags = self.hatch.AcDbHatch
        tags.append(DXFTag(999, 'MARKER'))  # add marker at the end
        self.hatch.set_seed_points([(1.0, 1.0), (2.0, 2.0)])
        index = tags.tag_index(98)  # pos of 'Number of seed points'
        self.assertEqual((10, (1.0, 1.0)), tags[index+1])
        self.assertEqual((10, (2.0, 2.0)), tags[index+2])
        self.assertEqual((999, 'MARKER'), tags[-1])  # marker still there?
