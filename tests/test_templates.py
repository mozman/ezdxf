#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test templates
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import os
import unittest

from ezdxf.templates import TemplateFinder


class TestTemplateFinder(unittest.TestCase):
    def test_filename(self):
        finder = TemplateFinder()
        self.assertEqual('ABC.dxf', finder.filename('ABC'))

    def test_filepath(self):
        finder = TemplateFinder()
        result = finder.filepath('AC1009')
        filename = os.path.join('ezdxf', 'templates', 'AC1009.dxf')
        self.assertTrue(result.endswith(filename))

    def test_set_templatepath(self):
        finder = TemplateFinder('templates')
        result = finder.filepath('AC1009')
        self.assertEqual(os.path.join('templates', 'AC1009.dxf'), result)

    def test_set_templatedir(self):
        finder = TemplateFinder('templates')
        finder.templatedir = 'templates2'
        self.assertEqual('templates2', finder.templatedir)


if __name__ == '__main__':
    unittest.main()