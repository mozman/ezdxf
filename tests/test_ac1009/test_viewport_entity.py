#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test viewport entity
# Created: 10.10.2015
# Copyright (C) 2015, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

from ezdxf.legacy.viewport import Viewport, _VPORT_TPL
from ezdxf.lldxf.classifiedtags import ClassifiedTags


class TestNewViewportEntity(unittest.TestCase):
    def setUp(self):
        self.viewport = Viewport(ClassifiedTags.from_text(_VPORT_TPL))

    def test_init_dxf_values(self):
        self.assertEqual((0, 0, 0), self.viewport.dxf.center)
        self.assertEqual(1.0, self.viewport.dxf.height)
        self.assertEqual(1.0, self.viewport.dxf.width)

    def test_init_viewport_data(self):
        vp_data = self.viewport.get_viewport_data()
        self.assertEqual((0, 0, 0), vp_data.view_target_point)
        self.assertEqual((0, 0, 0), vp_data.view_direction_vector)
        self.assertEqual(0, vp_data.view_twist_angle)
        self.assertEqual(1, vp_data.view_height)
        self.assertEqual((0, 0), vp_data.view_center_point)
        self.assertEqual(50, vp_data.perspective_lens_length)
        self.assertEqual(0, vp_data.front_clip_plane_z_value)
        self.assertEqual(0, vp_data.back_clip_plane_z_value)
        self.assertEqual(0, vp_data.view_mode)
        self.assertEqual(100, vp_data.circle_zoom)
        self.assertEqual(1, vp_data.fast_zoom)
        self.assertEqual(3, vp_data.ucs_icon)
        self.assertEqual(0, vp_data.snap)
        self.assertEqual(0, vp_data.grid)
        self.assertEqual(0, vp_data.snap_style)
        self.assertEqual(0, vp_data.snap_isopair)
        self.assertEqual(0, vp_data.snap_angle)
        self.assertEqual((0, 0), vp_data.snap_base_point)
        self.assertEqual((0.1, 0.1), vp_data.snap_spacing)
        self.assertEqual((0.1, 0.1), vp_data.grid_spacing)
        self.assertEqual(0, vp_data.hidden_plot)
        self.assertEqual([], vp_data.frozen_layers)
