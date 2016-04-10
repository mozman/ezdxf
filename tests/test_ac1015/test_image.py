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
from ezdxf.modern.image import ImageDef, Image
from ezdxf.lldxf.classifiedtags import ClassifiedTags

DWG = ezdxf.new('AC1015')


class TestImageDefFromText(unittest.TestCase):
    def setUp(self):
        self.tags = ClassifiedTags.from_text(IMAGE_DEF)
        self.image_def = ImageDef(self.tags, DWG)

    def test_imagedef_properties(self):
        self.assertEqual('IMAGEDEF', self.image_def.dxftype())

    def test_imagedef_dxf_attribs(self):
        self.assertEqual(0, self.image_def.dxf.class_version)
        self.assertEqual('mycat.jpg', self.image_def.dxf.filename)
        self.assertEqual((640., 360.), self.image_def.dxf.image_size)
        self.assertEqual((.01, .01), self.image_def.dxf.pixel_size)
        self.assertEqual(1, self.image_def.dxf.loaded)
        self.assertEqual(0, self.image_def.dxf.resolution_units)


class TestImageFromText(unittest.TestCase):
    def setUp(self):
        self.tags = ClassifiedTags.from_text(IMAGE)
        self.image = Image(self.tags, DWG)

    def test_image_properties(self):
        self.assertEqual('IMAGE', self.image.dxftype())

    def test_image_dxf_attribs(self):
        self.assertEqual((0., 0., 0.), self.image.dxf.insert)
        self.assertEqual((.01, 0., 0.), self.image.dxf.u_pixel)
        self.assertEqual((0., .01, 0.), self.image.dxf.v_pixel)
        self.assertEqual((640., 360.), self.image.dxf.image_size)
        self.assertEqual(7, self.image.dxf.flags)
        self.assertEqual(0, self.image.dxf.clipping)
        self.assertEqual(50, self.image.dxf.brightness)
        self.assertEqual(50, self.image.dxf.contrast)
        self.assertEqual(0, self.image.dxf.fade)
        self.assertEqual('DEAD', self.image.dxf.image_def_reactor)
        self.assertEqual(1, self.image.dxf.clipping_boundary_type)
        self.assertEqual(2, self.image.dxf.count_boundary_points)
        self.assertEqual([(0, 0), self.image.dxf.image_size], self.image.get_boundary_path())

    def test_get_boundary_path(self):
        self.assertEqual([(0, 0), (640, 360)], self.image.get_boundary_path())

    def test_reset_boundary_path(self):
        self.image.reset_boundary_path()
        self.assertEqual(2, self.image.dxf.count_boundary_points)
        self.assertEqual(3, self.image.dxf.flags)
        self.assertEqual([(0, 0), self.image.dxf.image_size], self.image.get_boundary_path())

    def test_set_boundary_path(self):
        self.image.set_boundary_path([(0, 0), (640, 180), (320, 360)])  # 3 vertices triangle
        self.assertEqual(3, self.image.dxf.count_boundary_points)
        self.assertEqual(2, self.image.dxf.clipping_boundary_type)
        self.assertEqual([(0, 0), (640, 180), (320, 360)], self.image.get_boundary_path())


class TestCreateNewImage(unittest.TestCase):
    def setUp(self):
        # setting up a drawing is expensive - use as few test methods as possible
        self.dwg = ezdxf.new('R2000')

    def test_new_image_def(self):
        rootdict = self.dwg.rootdict
        self.assertFalse('ACAD_IMAGE_DICT' in rootdict)
        imagedef = self.dwg.add_image_def('mycat.jpg', size_in_pixel=(640, 360))

        # check internals image_def_owner -> ACAD_IMAGE_DICT
        image_dict_handle = rootdict['ACAD_IMAGE_DICT']
        image_dict = self.dwg.get_dxf_entity(image_dict_handle)
        self.assertEqual(imagedef.dxf.owner, image_dict.dxf.handle)

        self.assertEqual('mycat.jpg', imagedef.dxf.filename)
        self.assertEqual((640., 360.), imagedef.dxf.image_size)

        # rest are default values
        self.assertEqual((.01, .01), imagedef.dxf.pixel_size)
        self.assertEqual(1, imagedef.dxf.loaded)
        self.assertEqual(0, imagedef.dxf.resolution_units)

    def test_new_image(self):
        msp = self.dwg.modelspace()
        image_def = self.dwg.add_image_def('mycat.jpg', size_in_pixel=(640, 360))
        image = msp.add_image(image_def=image_def, insert=(0, 0), size_in_units=(3.2, 1.8))
        self.assertEqual((0, 0, 0), image.dxf.insert)
        self.assertEqual((0.005, 0, 0), image.dxf.u_pixel)
        self.assertEqual((0., 0.005, 0), image.dxf.v_pixel)
        self.assertEqual((640, 360), image.dxf.image_size)
        self.assertEqual(image_def.dxf.handle, image.dxf.image_def)
        self.assertEqual(3, image.dxf.flags)
        self.assertEqual(0, image.dxf.clipping)
        self.assertEqual(2, image.dxf.count_boundary_points)
        self.assertEqual([(0, 0), image.dxf.image_size], image.get_boundary_path())

        image_def2 = image.get_image_def()
        self.assertEqual(image_def.dxf.handle, image_def2.dxf.handle)

        # does image def reactor exists
        reactor_handle = image.dxf.image_def_reactor
        self.assertTrue(reactor_handle in self.dwg.objects)
        reactor = self.dwg.get_dxf_entity(reactor_handle)
        self.assertEqual(image.dxf.handle, reactor.dxf.image)

        self.assertTrue(reactor_handle in image_def2.get_reactors(), "Reactor handle not in IMAGE_DEF reactors.")

        # delete image
        msp.delete_entity(image)
        self.assertFalse(reactor_handle in self.dwg.objects, "IMAGEDEF_REACTOR not deleted for objects section")
        self.assertFalse(reactor_handle in self.dwg.entitydb, "IMAGEDEF_REACTOR not deleted for entity database")
        self.assertFalse(reactor_handle in image_def2.get_reactors(), "Reactor handle not deleted from IMAGE_DEF reactors.")


IMAGE_DEF = """  0
IMAGEDEF
  5
DEAD
330
DEAD
100
AcDbRasterImageDef
 90
        0
  1
mycat.jpg
 10
640.0
 20
360.0
 11
0.01
 21
0.01
280
     1
281
     0
"""

IMAGE = """  0
IMAGE
  5
1DF
330
1F
100
AcDbEntity
  8
0
100
AcDbRasterImage
 90
        0
 10
0.0
 20
0.0
 30
0.0
 11
0.01
 21
0.0
 31
0.0
 12
0.0
 22
0.01
 32
0.0
 13
640.0
 23
360.0
340
DEAD
 70
     7
280
     0
281
    50
282
    50
283
     0
360
DEAD
 71
     1
 91
        2
 14
0.
 24
0.
 14
640.
 24
360.
"""