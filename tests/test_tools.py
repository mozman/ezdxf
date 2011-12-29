#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test tools
# Created: 27.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3
from __future__ import unicode_literals

import unittest

import ezdxf

from ezdxf.testtools import DrawingProxy

def getattributes(obj):
    return ( attr for attr in dir(obj) if not attr.startswith('_DrawingProxy__') )


class TestDrawingProxy(unittest.TestCase):
    def test_drawing(self):
        dwg = ezdxf.new('AC1024')
        for attr in getattributes(DrawingProxy('AC1024')):
            if not hasattr(dwg, attr):
                raise Exception("attribute '%s' of DrawingProxy() does not exist in Drawing() class" % attr)

if __name__=='__main__':
    unittest.main()