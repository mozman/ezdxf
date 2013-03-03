#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest
from io import StringIO

from ezdxf.testtools import DrawingProxy, normlines, Tags

from ezdxf.entitysection import EntitySection


class TestEntitySection(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingProxy('AC1009')
        self.section = EntitySection(Tags.fromtext(TESTENTITIES), self.dwg)

    def test_write(self):
        stream = StringIO()
        self.section.write(stream)
        result = stream.getvalue()
        stream.close()
        self.assertEqual(normlines(TESTENTITIES), normlines(result))

    def test_empty_section(self):
        section = EntitySection(Tags.fromtext(EMPTYSEC), self.dwg)
        stream = StringIO()
        section.write(stream)
        result = stream.getvalue()
        stream.close()
        self.assertEqual(EMPTYSEC, result)


EMPTYSEC = """  0
SECTION
  2
ENTITIES
  0
ENDSEC
"""

TESTENTITIES = """  0
SECTION
  2
ENTITIES
  0
VIEWPORT
  5
28B
 67
     1
  8
0
 10
4.7994580606
 20
4.0218994936
 30
0.0
 40
17.880612775
 41
8.9929997457
 68
     1
 69
     1
1001
ACAD
1000
MVIEW
1002
{
1070
    16
1010
0.0
1020
0.0
1030
0.0
1010
0.0
1020
0.0
1030
1.0
1040
0.0
1040
8.99299974
1040
4.79945806
1040
4.02189949
1040
50.0
1040
0.0
1040
0.0
1070
     0
1070
  1000
1070
     1
1070
     1
1070
     0
1070
     0
1070
     0
1070
     0
1040
0.0
1040
0.0
1040
0.0
1040
0.5
1040
0.5
1040
0.5
1040
0.5
1070
     0
1002
{
1002
}
1002
}
  0
VIEWPORT
  5
290
 67
     1
  8
VIEW_PORT
 10
4.8288665
 20
3.9999997
 30
0.0
 40
8.3999996
 41
6.3999996
 68
     2
 69
     2
1001
ACAD
1000
MVIEW
1002
{
1070
    16
1010
0.0
1020
0.0
1030
0.0
1010
0.0
1020
0.0
1030
1.0
1040
0.0
1040
6.399999
1040
6.0
1040
4.5
1040
50.0
1040
0.0
1040
0.0
1070
     0
1070
  1000
1070
     1
1070
     3
1070
     0
1070
     0
1070
     0
1070
     0
1040
0.0
1040
0.0
1040
0.0
1040
0.5
1040
0.5
1040
0.5
1040
0.5
1070
     0
1002
{
1002
}
1002
}
  0
ENDSEC
"""

if __name__ == '__main__':
    unittest.main()