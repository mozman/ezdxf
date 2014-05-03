# Author:  mozman -- <mozman@gmx.at>
# Purpose: test body, region, solid3d
# Created: 03.05.2014
# Copyright (C) 2014, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest
import ezdxf

DWG = ezdxf.new('AC1024')


class TestBody(unittest.TestCase):
    def setUp(self):
        self.layout = DWG.modelspace()

    def test_default_settings(self):
        body = self.layout.add_body()
        self.assertEqual('0', body.dxf.layer)

    def test_getting_acis_data(self):
        body = self.layout.add_body(acis_data=TEST_DATA.splitlines())
        self.assertEqual(TEST_DATA, "\n".join(body.get_acis_data()))

    def test_acis_data_context_manager(self):
        body = self.layout.add_body()
        with body.acis_data() as data:
            data.extend(TEST_DATA.splitlines())
        data = list(body.get_acis_data())
        self.assertEqual(TEST_DATA, "\n".join(data))


class TestRegion(unittest.TestCase):
    def setUp(self):
        self.layout = DWG.modelspace()

    def test_default_settings(self):
        region = self.layout.add_region()
        self.assertEqual('0', region.dxf.layer)

    def test_getting_acis_data(self):
        region = self.layout.add_region(acis_data=TEST_DATA.splitlines())
        self.assertEqual(TEST_DATA, "\n".join(region.get_acis_data()))


class Test3DSolid(unittest.TestCase):
    def setUp(self):
        self.layout = DWG.modelspace()

    def test_default_settings(self):
        _3dsolid = self.layout.add_3dsolid()
        self.assertEqual('0', _3dsolid.dxf.layer)
        self.assertEqual('0', _3dsolid.dxf.history)

    def test_getting_acis_data(self):
        _3dsolid = self.layout.add_3dsolid(acis_data=TEST_DATA.splitlines())
        self.assertEqual(TEST_DATA, "\n".join(_3dsolid.get_acis_data()))


TEST_DATA = """21200 115 2 26
16 Autodesk AutoCAD 19 ASM 217.0.0.4503 NT 0
1 9.9999999999999995e-007 1e-010
asmheader $-1 -1 @12 217.0.0.4503 #
body $2 -1 $-1 $3 $-1 $-1 #
ref_vt-eye-attrib $-1 -1 $-1 $-1 $1 $4 $5 #
lump $6 -1 $-1 $-1 $7 $1 #
eye_refinement $-1 -1 @5 grid  1 @3 tri 1 @4 surf 0 @3 adj 0 @4 grad 0 @9 postcheck 0 @4 stol 0.020115179941058159 @4 ntol 30 @4 dsil 0 @8 flatness 0 @7 pixarea 0 @4 hmax 0 @6 gridar 0 @5 mgrid 3000 @5 ugrid 0 @5 vgrid 0 @10 end_fields #
vertex_template $-1 -1 3 0 1 8 #"""

if __name__ == '__main__':
    unittest.main()
