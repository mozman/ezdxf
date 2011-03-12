#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test templates
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from ezdxf.templates import TemplateFinder

class TestTemplateFinder(unittest.TestCase):
    def test_filename(self):
        finder = TemplateFinder()
        self.assertEqual('ABC.dxf', finder.filename('ABC'))

    def test_filepath(self):
        finder = TemplateFinder()
        result = finder.filepath('AC1009')
        self.assertTrue(result.endswith(r'ezdxf\ezdxf\templates\AC1009.dxf'))

    def test_set_templatepath(self):
        finder = TemplateFinder(r'x:\templates')
        result = finder.filepath('AC1009')
        self.assertEqual(r'x:\templates\AC1009.dxf', result)

    def test_set_templatedir(self):
        finder = TemplateFinder(r'x:\templates')
        finder.templatedir = r'y:\templates'
        self.assertEqual(r'y:\templates', finder.templatedir)

if __name__=='__main__':
    unittest.main()