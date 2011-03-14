#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test blocks section
# Created: 14.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest
from io import StringIO

from ezdxf.handle import HandleGenerator
from ezdxf.tags import Tags

from ezdxf.blockssection import BlocksSection

class DrawingMock:
    entitydb = dict()
    handles = HandleGenerator()

def normlines(text):
    lines = text.split('\n')
    return [line.strip() for line in lines]

class TestBlocksSection(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingMock()
        self.section = BlocksSection(Tags.fromtext(TESTBLOCKS), self.dwg)

    def test_write(self):
        stream = StringIO()
        self.section.write(stream)
        result = stream.getvalue()
        stream.close()
        self.assertEqual(normlines(TESTBLOCKS), normlines(result))

    def test_empty_section(self):
        section = BlocksSection(Tags.fromtext(EMPTYSEC), self.dwg)
        stream = StringIO()
        section.write(stream)
        result = stream.getvalue()
        stream.close()
        self.assertEqual(EMPTYSEC, result)

EMPTYSEC = """  0
SECTION
  2
BLOCKS
  0
ENDSEC
"""

TESTBLOCKS = """  0
SECTION
  2
BLOCKS
  0
BLOCK
  8
0
  2
$MODEL_SPACE
 70
     0
 10
0.0
 20
0.0
 30
0.0
  3
$MODEL_SPACE
  1

  0
ENDBLK
  5
21
  8
0
  0
BLOCK
 67
     1
  8
0
  2
$PAPER_SPACE
 70
     0
 10
0.0
 20
0.0
 30
0.0
  3
$PAPER_SPACE
  1

  0
ENDBLK
  5
5B
 67
     1
  8
0
  0
BLOCK
  8
0
  2
_ARCHTICK
 70
     0
 10
0.0
 20
0.0
 30
0.0
  3
_ARCHTICK
  1

  0
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
  0
ENDBLK
  5
23B
  8
0
  0
BLOCK
  8
0
  2
_OPEN30
 70
     0
 10
0.0
 20
0.0
 30
0.0
  3
_OPEN30
  1

  0
LINE
  5
23D
  8
0
  6
BYBLOCK
 62
     0
 10
-1.0
 20
0.26794919
 30
0.0
 11
0.0
 21
0.0
 31
0.0
  0
LINE
  5
23E
  8
0
  6
BYBLOCK
 62
     0
 10
0.0
 20
0.0
 30
0.0
 11
-1.0
 21
-0.26794919
 31
0.0
  0
LINE
  5
23F
  8
0
  6
BYBLOCK
 62
     0
 10
0.0
 20
0.0
 30
0.0
 11
-1.0
 21
0.0
 31
0.0
  0
ENDBLK
  5
241
  8
0
  0
ENDSEC
"""

if __name__=='__main__':
    unittest.main()