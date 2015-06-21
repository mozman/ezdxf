#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test hatch entity
# Created: 25.05.2015
# Copyright (C) 2015, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

from ezdxf.modern.hatch import Hatch, _HATCH_TPL
from ezdxf.classifiedtags import ClassifiedTags, DXFTag

class TestHatch(unittest.TestCase):
    def setUp(self):
        tags = ClassifiedTags.from_text(_HATCH_TPL)
        self.hatch = Hatch(tags)

    def test_default_settings(self):
        hatch = self.hatch
        self.assertEqual('0', hatch.dxf.layer)
        self.assertEqual(1, hatch.dxf.color)
        self.assertEqual('BYLAYER', hatch.dxf.linetype)
        self.assertEqual(1.0, hatch.dxf.ltscale)
        self.assertEqual(0, hatch.dxf.invisible)
        self.assertEqual((0.0, 0.0, 1.0), hatch.dxf.extrusion)
        self.assertEqual((0.0, 0.0, 0.0), hatch.dxf.elevation)

    def test_default_hatch_settings(self):
        hatch = self.hatch
        self.assertEqual(1, hatch.dxf.solid_fill)
        self.assertEqual(1, hatch.dxf.hatch_style)
        self.assertEqual(1, hatch.dxf.pattern_type)
        self.assertEqual(0.0, hatch.dxf.pattern_angle)
        self.assertEqual(1.0, hatch.dxf.pattern_scale)
        self.assertEqual(0, hatch.dxf.pattern_double)
        self.assertEqual(1, hatch.dxf.n_seed_points)

    def test_get_seed_points(self):
        hatch = self.hatch
        seed_points = hatch.get_seed_points()
        self.assertEqual(1, len(seed_points))
        self.assertEqual((0., 0.), seed_points[0])

    def test_set_seed_points(self):
        hatch = self.hatch
        seed_points = [(1.0, 1.0), (2.0, 2.0)]
        hatch.set_seed_points(seed_points)
        self.assertEqual(2, hatch.dxf.n_seed_points)
        new_seed_points = hatch.get_seed_points()
        self.assertEqual(seed_points, new_seed_points)
        # low level test
        tags = hatch.AcDbHatch
        index = tags.tag_index(98)  # pos of 'Number of seed points'
        self.assertEqual((1.0, 1.0), tags[index+1].value)
        self.assertEqual((2.0, 2.0), tags[index+2].value)

    def test_set_seed_points_low_level(self):
        tags = self.hatch.AcDbHatch
        tags.append(DXFTag(999, 'MARKER'))  # add marker at the end
        self.hatch.set_seed_points([(1.0, 1.0), (2.0, 2.0)])
        index = tags.tag_index(98)  # pos of 'Number of seed points'
        self.assertEqual((10, (1.0, 1.0)), tags[index+1])
        self.assertEqual((10, (2.0, 2.0)), tags[index+2])
        self.assertEqual((999, 'MARKER'), tags[-1])  # marker still there?

class TestBoundaryPathData(unittest.TestCase):
    def setUp(self):
        tags = ClassifiedTags.from_text(PATH_HATCH)
        self.hatch = Hatch(tags)

    def test_path_count(self):
        with self.hatch.edit_boundary() as editor:
            self.assertEqual(1, len(editor.paths), "invalid boundary path count")

    def test_remove_all_paths(self):
        with self.hatch.edit_boundary() as editor:
            editor.clear()
            self.assertEqual(0, len(editor.paths), "invalid boundary path count")


class TestCreateBoundaryPathData(unittest.TestCase):
    def setUp(self):
        tags = ClassifiedTags.from_text(_HATCH_TPL)
        self.hatch = Hatch(tags)

    def test_add_polyline_path(self):
        with self.hatch.edit_boundary() as editor:
            new_path = editor.add_polyline_path([(0, 0), (0, 1), (1, 1), (1, 0)])
            self.assertEqual('PolylinePath', new_path.PATH_TYPE, "invalid path type")
            self.assertEqual(4, len(new_path.vertices), "invalid vertex count")

        # now check the created entity
        with self.hatch.edit_boundary() as editor:
            self.assertEqual(1, len(editor.paths))
            path = editor.paths[0]
            self.assertEqual('PolylinePath', path.PATH_TYPE, "invalid path type")
            self.assertEqual(4, len(path.vertices), "invalid vertex count")
            # vertex format: x, y, bulge_value
            self.assertEqual((0, 0, 0), path.vertices[0], "invalid first vertex")
            self.assertEqual((1, 0, 0), path.vertices[3], "invalid last vertex")
            self.assertTrue(path.is_closed)

    def test_add_edge_path(self):  # TODO
        pass


class TestPolylinePath(unittest.TestCase):
    def setUp(self):
        tags = ClassifiedTags.from_text(PATH_HATCH)
        self.hatch = Hatch(tags)

    def testPolylinePathAttribs(self):
        with self.hatch.edit_boundary() as editor:
            path = editor.paths[0]  # test first boundary path
            self.assertEqual('PolylinePath', path.PATH_TYPE, "invalid path type")
            self.assertEqual(4, len(path.vertices))
            self.assertFalse(path.has_bulge)
            self.assertTrue(path.is_closed)
            self.assertEqual(7, path.path_type_flags, "unexpected path type flags")

    def testPolylinePathVertices(self):
        with self.hatch.edit_boundary() as editor:
            path = editor.paths[0]  # test first boundary path
            self.assertEqual('PolylinePath', path.PATH_TYPE, "invalid path type")
            self.assertEqual(4, len(path.vertices))
            # vertex format: x, y, bulge_value
            self.assertEqual((10, 10, 0), path.vertices[0], "invalid first vertex")
            self.assertEqual((10, 0, 0), path.vertices[3], "invalid last vertex")

class TestEdgeHatch(unittest.TestCase):
    def setUp(self):
        tags = ClassifiedTags.from_text(EDGE_HATCH)
        self.hatch = Hatch(tags)

class TestEdgeHatchWithSpline(unittest.TestCase):
    def setUp(self):
        tags = ClassifiedTags.from_text(EDGE_HATCH_WITH_SPLINE)
        self.hatch = Hatch(tags)

PATH_HATCH = """  0
HATCH
  5
27C
330
1F
100
AcDbEntity
  8
0
 62
     1
100
AcDbHatch
 10
0.0
 20
0.0
 30
0.0
210
0.0
220
0.0
230
1.0
  2
SOLID
 70
     1
 71
     0
 91
        1
 92
        7
 72
     0
 73
     1
 93
        4
 10
10.0
 20
10.0
 10
0.0
 20
10.0
 10
0.0
 20
0.0
 10
10.0
 20
0.0
 97
        0
 75
     1
 76
     1
 47
0.0442352806926743
 98
        1
 10
4.826903383179796
 20
4.715694827530256
450
        0
451
        0
460
0.0
461
0.0
452
        0
462
1.0
453
        2
463
0.0
 63
     5
421
      255
463
1.0
 63
     2
421
 16776960
470
LINEAR
1001
GradientColor1ACI
1070
     5
1001
GradientColor2ACI
1070
     2
1001
ACAD
1010
0.0
1020
0.0
1030
0.0
"""

EDGE_HATCH = """  0
HATCH
  5
1FE
330
1F
100
AcDbEntity
  8
0
100
AcDbHatch
 10
0.0
 20
0.0
 30
0.0
210
0.0
220
0.0
230
1.0
  2
SOLID
 70
     1
 71
     1
 91
        1
 92
        5
 93
        8
 72
     3
 10
10.0
 20
5.0
 11
3.0
 21
0.0
 40
0.3333333333333333
 50
270
 51
450
 73
     1
 72
     1
 10
10.0
 20
6.0
 11
10.0
 21
10.0
 72
     1
 10
10.0
 20
10.0
 11
6.0
 21
10.0
 72
     2
 10
5.0
 20
10.0
 40
1.0
 50
360.0
 51
540.0
 73
     0
 72
     1
 10
4.0
 20
10.0
 11
0.0
 21
10.0
 72
     1
 10
0.0
 20
10.0
 11
0.0
 21
0.0
 72
     1
 10
0.0
 20
0.0
 11
10.0
 21
0.0
 72
     1
 10
10.0
 20
0.0
 11
10.0
 21
4.0
 97
        8
330
1E7
330
1EC
330
1E4
330
1E6
330
1EA
330
1E5
330
1E2
330
1E3
 75
     1
 76
     1
 47
0.0226465124087611
 98
        1
 10
5.15694040451099
 20
5.079032000141936
450
        0
451
        0
460
0.0
461
0.0
452
        0
462
1.0
453
        2
463
0.0
 63
     5
421
      255
463
1.0
 63
     2
421
 16776960
470
LINEAR
1001
GradientColor1ACI
1070
     5
1001
GradientColor2ACI
1070
     2
1001
ACAD
1010
0.0
1020
0.0
1030
0.0
"""

EDGE_HATCH_WITH_SPLINE ="""  0
HATCH
  5
220
330
1F
100
AcDbEntity
  8
0
 62
     1
100
AcDbHatch
 10
0.0
 20
0.0
 30
0.0
210
0.0
220
0.0
230
1.0
  2
SOLID
 70
     1
 71
     1
 91
        1
 92
        5
 93
        4
 72
     1
 10
10.0
 20
10.0
 11
0.0
 21
10.0
 72
     4
 94
        3
 73
     0
 74
     0
 95
       10
 96
        6
 40
0.0
 40
0.0
 40
0.0
 40
0.0
 40
3.354101966249684
 40
7.596742653368969
 40
11.86874452602773
 40
11.86874452602773
 40
11.86874452602773
 40
11.86874452602773
 10
0.0
 20
10.0
 10
0.8761452790665735
 20
8.935160214313272
 10
2.860536415354832
 20
6.523392802252294
 10
-3.08307347911064
 20
4.314363374126372
 10
-1.030050983735315
 20
1.441423393837641
 10
0.0
 20
0.0
 97
        4
 11
0.0
 21
10.0
 11
1.5
 21
7.0
 11
-1.5
 21
4.0
 11
0.0
 21
0.0
 12
0.0
 22
0.0
 13
0.0
 23
0.0
 72
     1
 10
0.0
 20
0.0
 11
10.0
 21
0.0
 72
     1
 10
10.0
 20
0.0
 11
10.0
 21
10.0
 97
        4
330
215
330
217
330
213
330
214
 75
     1
 76
     1
 47
0.0365335049696054
 98
        1
 10
5.5
 20
4.5
450
        0
451
        0
460
0.0
461
0.0
452
        0
462
1.0
453
        2
463
0.0
 63
     5
421
      255
463
1.0
 63
     2
421
 16776960
470
LINEAR
1001
GradientColor1ACI
1070
     5
1001
GradientColor2ACI
1070
     2
1001
ACAD
1010
0.0
1020
0.0
1030
0.0
"""