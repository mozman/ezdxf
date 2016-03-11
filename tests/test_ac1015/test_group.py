#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test dxf group and group table
# Created: 16.07.2015
# Copyright (C) 2015, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest
import ezdxf


class TestDXFGroups(unittest.TestCase):
    def setUp(self):
        self.dwg = ezdxf.new('AC1015')  # min. required DXF version
        self.groups = self.dwg.groups

    def test_group_table_is_empty(self):
        self.assertEqual(0, len(self.groups))

    def test_create_new_group(self):
        g = self.groups.new('MyGroup', description="The group description.")
        self.assertEqual('GROUP', g.dxftype())
        self.assertTrue('MyGroup' in self.groups)
        self.assertEqual(0, g.dxf.unnamed, "Named group has wrong unnamed attribute.")
        self.assertEqual(1, g.dxf.selectable, "Group should be selectable by default.")
        self.assertEqual("The group description.", g.dxf.description)
        self.assertEqual(1, len(self.groups))
        self.groups.clear()
        self.assertEqual(0, len(self.groups))

    def test_create_unnamed_group(self):
        g = self.groups.new()
        self.assertEqual('GROUP', g.dxftype())
        self.assertTrue('*A1' in self.groups)
        self.assertEqual(1, g.dxf.unnamed, "Unnamed group has wrong unnamed attribute.")
        self.assertEqual(1, g.dxf.selectable, "Group should be selectable by default.")
        self.assertEqual("", g.dxf.description, "Group description should be '' by default.")
        self.assertEqual(1, len(self.groups))
        self.groups.clear()
        self.assertEqual(0, len(self.groups))

    def test_delete_group_by_entity(self):
        g = self.groups.new('MyGroup')
        self.groups.delete(g)
        self.assertEqual(0, len(self.groups))

    def test_delete_group_by_name(self):
        self.groups.new('MyGroup')
        self.groups.delete('MyGroup')
        self.assertEqual(0, len(self.groups))


class TestDXFGroup(unittest.TestCase):
    def setUp(self):
        self.dwg = ezdxf.new('AC1015')  # min. required DXF version
        self.groups = self.dwg.groups

    def test_add_entities(self):
        group = self.groups.new()
        # the group itself is not an entity space, DXF entities has to be placed in model space, paper space
        # or in a block
        msp = self.dwg.modelspace()
        with group.edit_data() as e:  # e is a standard Python list of DXF entities
            line = msp.add_line((0, 0), (3, 0))
            e.append(line)
            e.append(msp.add_circle((0, 0), radius=2))

        self.assertEqual(2, len(group))
        self.assertTrue(line in group)

        ungrouped_line = msp.add_line((0, 1), (3, 1))
        self.assertFalse(ungrouped_line in group)

        group.clear()
        self.assertEqual(0, len(group))
