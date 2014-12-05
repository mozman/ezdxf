#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test reading DXF files from zip archive
# Created: 02.05.2014
# Copyright (C) 2014, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals

import unittest
import os

import ezdxf

ZIPFILE = "read_zip_test.zip"


def get_zip_path(zip_file_name):
    test_path = os.path.dirname(__file__)
    zip_path = os.path.join(test_path, zip_file_name)
    return zip_path


@unittest.skipUnless(os.path.exists(get_zip_path(ZIPFILE)), "Skipped TestReadZip(): file '{}' not found.".format(get_zip_path(ZIPFILE)))
class TestReadZip(unittest.TestCase):

    def test_read_ac1009(self):
        dwg = ezdxf.readzip(get_zip_path(ZIPFILE), 'AC1009.dxf')
        msp = dwg.modelspace()
        lines = msp.query('LINE')
        self.assertEqual(255, len(lines))


if __name__ == '__main__':
    unittest.main()