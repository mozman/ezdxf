#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test layout creation
# Created: 25.04.2014
# Copyright (C) 2014, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

import ezdxf

DWG = ezdxf.new('AC1015')


class TestCreateLayout(unittest.TestCase):
    def test_create_new_layout(self):
        new_layout = DWG.layouts.create('mozman_layout')
        self.assertEqual('mozman_layout', new_layout.name)

    def test_error_creating_layout_with_existing_name(self):
        with self.assertRaises(ValueError):
            DWG.layouts.create('Model')

