#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test image and imagedef entity
# Created: 13.03.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

import ezdxf
from ezdxf.modern.underlay import PdfDefinition, PdfUnderlay
from ezdxf.lldxf.classifiedtags import ClassifiedTags

DWG = ezdxf.new('AC1015')


class TestUnderlayDefFromText(unittest.TestCase):
    def setUp(self):
        self.tags = ClassifiedTags.from_text(PDF_DEFINITION)
        self.pdf_def = PdfDefinition(self.tags, DWG)

    def test_imagedef_properties(self):
        self.assertEqual('PDFDEFINITION', self.pdf_def.dxftype())
        self.assertEqual('PDFUNDERLAY', self.pdf_def.entity_name)

    def test_imagedef_dxf_attribs(self):
        self.assertEqual('underlay.pdf', self.pdf_def.dxf.filename)
        self.assertEqual('underlay_key', self.pdf_def.dxf.name)


class TestUnderlayFromText(unittest.TestCase):
    def setUp(self):
        self.tags = ClassifiedTags.from_text(PDF_UNDERLAY)
        self.pdf = PdfUnderlay(self.tags, DWG)

    def test_image_properties(self):
        self.assertEqual('PDFUNDERLAY', self.pdf.dxftype())

    def test_image_dxf_attribs(self):
        self.assertEqual((0., 0., 0.), self.pdf.dxf.insert)
        self.assertEqual(2.5, self.pdf.dxf.scale_x)
        self.assertEqual(2.5, self.pdf.dxf.scale_y)
        self.assertEqual(2.5, self.pdf.dxf.scale_z)
        self.assertEqual((2.5, 2.5, 2.5), self.pdf.scale)
        self.assertEqual(2, self.pdf.dxf.flags)
        self.assertFalse(self.pdf.clipping)
        self.assertTrue(self.pdf.on)
        self.assertFalse(self.pdf.monochrome)
        self.assertFalse(self.pdf.adjust_for_background)
        self.assertEqual(100, self.pdf.dxf.contrast)
        self.assertEqual(0, self.pdf.dxf.fade)
        self.assertEqual('DEAD1', self.pdf.dxf.underlay_def)

    def test_get_boundary_path(self):
        self.assertEqual([], self.pdf.get_boundary_path())

    def test_reset_boundary_path(self):
        self.pdf.reset_boundary_path()
        self.assertEqual([], self.pdf.get_boundary_path())
        self.assertFalse(self.pdf.clipping)

    def test_set_boundary_path(self):
        self.pdf.set_boundary_path([(0, 0), (640, 180), (320, 360)])  # 3 vertices triangle
        self.assertTrue(self.pdf.clipping)
        self.assertEqual([(0, 0), (640, 180), (320, 360)], self.pdf.get_boundary_path())

    def test_set_scale(self):
        self.pdf.scale = (1.2, 1.3, 1.4)
        self.assertEqual((1.2, 1.3, 1.4), self.pdf.scale)

        self.pdf.scale = 1.7
        self.assertEqual((1.7, 1.7, 1.7), self.pdf.scale)


class TestCreateNewUnderlay(unittest.TestCase):
    def setUp(self):
        # setting up a drawing is expensive - use as few test methods as possible
        self.dwg = ezdxf.new('R2000')

    def test_new_pdf_underlay_def(self):
        rootdict = self.dwg.rootdict
        self.assertFalse('ACAD_PDFDEFINITIONS' in rootdict)
        underlay_def = self.dwg.add_underlay_def('underlay.pdf', format='pdf', name='u1')

        # check internals pdf_def_owner -> ACAD_PDFDEFINITIONS
        pdf_dict_handle = rootdict['ACAD_PDFDEFINITIONS']
        pdf_dict = self.dwg.get_dxf_entity(pdf_dict_handle)
        self.assertEqual(underlay_def.dxf.owner, pdf_dict.dxf.handle)

        self.assertEqual('underlay.pdf', underlay_def.dxf.filename)
        self.assertEqual('u1', underlay_def.dxf.name)

    def test_new_image(self):
        msp = self.dwg.modelspace()
        underlay_def = self.dwg.add_underlay_def('underlay.pdf')
        underlay = msp.add_underlay(underlay_def, insert=(0, 0, 0), scale=2)
        self.assertEqual((0, 0, 0), underlay.dxf.insert)
        self.assertEqual(2, underlay.dxf.scale_x)
        self.assertEqual(2, underlay.dxf.scale_y)
        self.assertEqual(2, underlay.dxf.scale_z)
        self.assertEqual(underlay_def.dxf.handle, underlay.dxf.underlay_def)
        self.assertFalse(underlay.clipping)
        self.assertTrue(underlay.on)
        self.assertFalse(underlay.monochrome)
        self.assertFalse(underlay.adjust_for_background)
        self.assertEqual(2, underlay.dxf.flags)

        underlay_def2 = underlay.get_underlay_def()
        self.assertEqual(underlay_def.dxf.handle, underlay_def2.dxf.handle)


PDF_DEFINITION = """  0
PDFDEFINITION
  5
DEAD1
330
DEAD2
100
AcDbUnderlayDefinition
  1
underlay.pdf
  2
underlay_key
"""

PDF_UNDERLAY = """  0
PDFUNDERLAY
  5
DEAD3
330
DEAD4
100
AcDbEntity
  8
0
100
AcDbUnderlayReference
340
DEAD1
 10
0.0
 20
0.0
 30
0.0
 41
2.5
 42
2.5
 43
2.5
280
  2
281
   100
282
     0
"""