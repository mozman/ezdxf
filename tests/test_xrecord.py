# encoding: utf-8
# Copyright (C) 2013, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals

import unittest

from ezdxf.testtools import ClassifiedTags, DXFTag
from ezdxf.modern.dxfobjects import XRecord


class TestXRecord(unittest.TestCase):
    def setUp(self):
        self.xrecord = XRecord(ClassifiedTags.from_text(XRECORD1))

    def test_handle(self):
        self.assertEqual('43A', self.xrecord.dxf.handle)

    def test_parent_handle(self):
        self.assertEqual('28C', self.xrecord.dxf.owner)

    def test_cloning_parameter(self):
        self.assertEqual(1, self.xrecord.dxf.cloning)

    def test_get_data(self):
        self.assertEqual(DXFTag(102, 'SHADEPLOT'), self.xrecord[0])
        self.assertEqual(DXFTag(70, 0), self.xrecord[1])

    def test_last_data(self):
        self.assertEqual(DXFTag(70, 0), self.xrecord[-1])

    def test_iter_data(self):
        tags = list(self.xrecord)
        self.assertEqual(DXFTag(102, 'SHADEPLOT'), tags[0])
        self.assertEqual(DXFTag(70, 0), tags[1])

    def test_len(self):
        self.assertEqual(2, len(self.xrecord))

    def test_set_data(self):
        self.xrecord[0] = DXFTag(103, 'MOZMAN')
        self.assertEqual(DXFTag(103, 'MOZMAN'), self.xrecord[0])
        self.assertEqual(DXFTag(70, 0), self.xrecord[1])

    def test_append_data(self):
        self.xrecord.append(DXFTag(103, 'MOZMAN'))
        self.assertEqual(DXFTag(103, 'MOZMAN'), self.xrecord[-1])


XRECORD1 = """  0
XRECORD
  5
43A
102
{ACAD_REACTORS
330
28C
102
}
330
28C
100
AcDbXrecord
280
     1
102
SHADEPLOT
 70
     0
"""

if __name__ == '__main__':
    unittest.main()
