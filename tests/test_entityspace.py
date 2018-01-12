#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test entity space
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

from ezdxf.tools.test import DrawingProxy
from ezdxf.entityspace import EntitySpace
from ezdxf.lldxf.tags import internal_tag_compiler, group_tags


class TestEntitySpace(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingProxy('AC1009')
        self.space = EntitySpace(self.dwg.entitydb)

    def test_add(self):
        for group in group_tags(internal_tag_compiler(TESTENTITIES)):
            self.space.store_tags(group)
        self.assertEqual(4, len(self.space))


TESTENTITIES = """  0
POLYLINE
  5
239
  8
0
  6
BYBLOCK
 62
     0
 66
     1
 10
0.0
 20
0.0
 30
0.0
 40
0.15
 41
0.15
  0
VERTEX
  5
403
  8
0
  6
BYBLOCK
 62
     0
 10
-0.5
 20
-0.5
 30
0.0
  0
VERTEX
  5
404
  8
0
  6
BYBLOCK
 62
     0
 10
0.5
 20
0.5
 30
0.0
  0
SEQEND
  5
405
  8
0
  6
BYBLOCK
 62
     0
"""

if __name__ == '__main__':
    unittest.main()