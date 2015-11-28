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


def is_layout_in_object_section(layout):
    return layout.dxf.handle in DWG.objects


def is_layout_in_dxf_layout_management_table(layout):
    dxf_layout_management_table_handle = DWG.rootdict['ACAD_LAYOUT']
    dxf_layout_management_table = DWG.dxffactory.wrap_handle(dxf_layout_management_table_handle)
    return layout.name in dxf_layout_management_table


def block_record_for_layout_exist(layout):
    for block_record in DWG.sections.tables.block_records:
        if block_record.dxf.layout == layout.dxf.handle:
            return True
    return False


def block_for_layout_exist(layout):
    for block in DWG.blocks:
        if block.block_record_handle == layout.layout_key:
            return True
    return False


class TestCreateLayout(unittest.TestCase):
    def test_create_new_layout(self):
        DWG.create_layout('mozman_layout')
        new_layout = DWG.layouts.get('mozman_layout')
        self.assertEqual('mozman_layout', new_layout.name)
        self.assertTrue(is_layout_in_object_section(new_layout))
        self.assertTrue(is_layout_in_dxf_layout_management_table(new_layout))
        self.assertTrue(block_record_for_layout_exist(new_layout))
        self.assertTrue(block_for_layout_exist(new_layout))

    def test_error_creating_layout_with_existing_name(self):
        with self.assertRaises(ValueError):
            DWG.create_layout('Model')


class TestLayoutMangement(unittest.TestCase):
    def test_create_and_delete_new_layout(self):
        new_layout = DWG.create_layout('mozman_layout_2')
        self.assertEqual('mozman_layout_2', new_layout.name)
        self.assertTrue(is_layout_in_object_section(new_layout))
        self.assertTrue(is_layout_in_dxf_layout_management_table(new_layout))
        self.assertTrue(block_record_for_layout_exist(new_layout))
        self.assertTrue(block_for_layout_exist(new_layout))

        DWG.delete_layout(new_layout.name)

        self.assertFalse(is_layout_in_object_section(new_layout))
        self.assertFalse(is_layout_in_dxf_layout_management_table(new_layout))
        self.assertFalse(block_record_for_layout_exist(new_layout))
        self.assertFalse(block_for_layout_exist(new_layout))
        self.assertFalse(new_layout.dxf.handle in DWG.entitydb)

    def test_set_active_layout(self):
        new_layout = DWG.create_layout('mozman_layout_3')
        DWG.layouts.set_active_layout('mozman_layout_3')
        self.assertEqual('*Paper_Space', new_layout.block_record_name)
        self.assertEqual(new_layout.layout_key, DWG.get_active_layout_key())
