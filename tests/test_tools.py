#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test tools
# Created: 27.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

import ezdxf

from tools import DrawingProxy

def checkattribs(obj):
    return ( attr for attr in dir(obj) if not attr.startswith('_DrawingProxy__') )

class TestDrawingProxy(unittest.TestCase):
    def test_drawing(self):
        dwg = ezdxf.new('AC1024')
        for attr in checkattribs(DrawingProxy):
            if not hasattr(dwg, attr):
                raise Exception("Attribute '%s' of DrawingProxy() does not exist in Drawing() class" % attr)

if __name__=='__main__':
    unittest.main()