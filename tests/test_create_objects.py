#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test create new objects / needs an drawing with objects section
# Created: 07.03.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

import ezdxf
from ezdxf.lldxf.tags import Tags
from ezdxf.sections.objects import ObjectsSection

# for fast running tests, just create drawing one time and reset objects sections

DXF_DRAWING = ezdxf.new('AC1015')
wrap_handle = DXF_DRAWING.dxffactory.wrap_handle

_OBJECT_TABLE_NAMES = [
    "ACAD_COLOR",
    "ACAD_GROUP",
    "ACAD_LAYOUT",
    "ACAD_MATERIAL",
    "ACAD_MLEADERSTYLE",
    "ACAD_MLINESTYLE",
    "ACAD_PLOTSETTINGS",
    "ACAD_PLOTSTYLENAME",
    "ACAD_SCALELIST",
    "ACAD_TABLESTYLE",
    "ACAD_VISUALSTYLE",
]


class TestObjectCreation(unittest.TestCase):  # needs a valid objects section
    def setUp(self):
        self.objects = ObjectsSection(Tags.from_text(EMPTYSEC), DXF_DRAWING)
        DXF_DRAWING.sections._sections['objects'] = self.objects   # reset objects section

    def get_rootdict(self):
        rootdict = self.objects.setup_rootdict()
        self.objects.setup_objects_management_tables(rootdict)
        return rootdict

    def test_setup_rootdict(self):
        rootdict = self.objects.setup_rootdict()
        self.assertEqual('DICTIONARY', rootdict.dxftype())

    def test_add_new_sub_dict(self):
        rootdict = self.get_rootdict()
        new_dict = rootdict.add_new_dict('A_SUB_DICT')
        self.assertEqual('DICTIONARY', new_dict.dxftype())
        self.assertEqual(0, len(new_dict))
        self.assertTrue('A_SUB_DICT' in rootdict)
        self.assertEqual(rootdict.dxf.handle, new_dict.dxf.owner)

    def test_required_tables_exists(self):
        rootdict = self.get_rootdict()
        self.objects.setup_objects_management_tables(rootdict)

        for table_name in _OBJECT_TABLE_NAMES:
            self.assertTrue(table_name in rootdict, "table %s not found." % table_name)

    def test_new_plot_style_name_table(self):
        rootdict = self.get_rootdict()
        plot_style_name_table = wrap_handle(rootdict["ACAD_PLOTSTYLENAME"])
        self.assertEqual('ACDBDICTIONARYWDFLT', plot_style_name_table.dxftype())
        place_holder = wrap_handle(plot_style_name_table['Normal'])
        self.assertEqual('ACDBPLACEHOLDER', place_holder.dxftype())
        self.assertEqual(place_holder.dxf.owner, plot_style_name_table.dxf.handle)


EMPTYSEC = """  0
SECTION
  2
OBJECTS
  0
ENDSEC
"""

if __name__ == '__main__':
    unittest.main()
