#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test basic graphic entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from ezdxf.handle import HandleGenerator
from ezdxf.dxffactory import dxffactory

class DrawingProxy:
    def __init__(self):
        self.handles = HandleGenerator()
        self.entitydb = {}
        self.dxffactory = dxffactory('AC1015')
        self.dxffactory.drawing = self


class TestLine(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingProxy()
        self.factory = self.dwg.dxffactory

    def test_create_line(self):
        line = self.factory.line((0, 0), (1, 1))
        self.assertEqual((0.,0.), line.start)
        self.assertEqual((1.,1.), line.end)

if __name__=='__main__':
    unittest.main()