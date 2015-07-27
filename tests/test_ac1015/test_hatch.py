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
from ezdxf.lldxf.classifiedtags import ClassifiedTags, DXFTag

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

    def test_path_count(self):
        with self.hatch.edit_boundary() as editor:
            self.assertEqual(1, len(editor.paths), "invalid boundary path count")

    def test_path_type(self):
        with self.hatch.edit_boundary() as editor:
            path = editor.paths[0]
            self.assertEqual('EdgePath', path.PATH_TYPE, "invalid path type")

    def test_path_edges(self):
        with self.hatch.edit_boundary() as editor:
            path = editor.paths[0]
            edge = path.edges[0]
            self.assertEqual('EllipseEdge', edge.EDGE_TYPE, "invalid edge type for 1. edge")
            self.assertEqual((10, 5), edge.center)
            self.assertEqual((3, 0), edge.major_axis_vector)
            self.assertEqual(1./3., edge.minor_axis_length)
            self.assertEqual(270, edge.start_angle)
            self.assertEqual(450, edge.end_angle)  # this value was created by AutoCAD == 90 degree
            self.assertEqual(1, edge.is_counter_clockwise)

            edge = path.edges[1]
            self.assertEqual('LineEdge', edge.EDGE_TYPE, "invalid edge type for 2. edge")
            self.assertEqual((10, 6), edge.start)
            self.assertEqual((10, 10), edge.end)

            edge = path.edges[2]
            self.assertEqual('LineEdge', edge.EDGE_TYPE, "invalid edge type for 3. edge")
            self.assertEqual((10, 10), edge.start)
            self.assertEqual((6, 10), edge.end)

            edge = path.edges[3]
            self.assertEqual('ArcEdge', edge.EDGE_TYPE, "invalid edge type for 4. edge")
            self.assertEqual((5, 10), edge.center)
            self.assertEqual(1, edge.radius)
            self.assertEqual(360, edge.start_angle)  # this value was created by AutoCAD == 0 degree
            self.assertEqual(540, edge.end_angle)  # this value was created by AutoCAD == 180 degree
            self.assertEqual(0, edge.is_counter_clockwise)

            edge = path.edges[4]
            self.assertEqual('LineEdge', edge.EDGE_TYPE, "invalid edge type for 5. edge")
            self.assertEqual((4, 10), edge.start)
            self.assertEqual((0, 10), edge.end)

            edge = path.edges[5]
            self.assertEqual('LineEdge', edge.EDGE_TYPE, "invalid edge type for 6. edge")
            self.assertEqual((0, 10), edge.start)
            self.assertEqual((0, 0), edge.end)

            edge = path.edges[6]
            self.assertEqual('LineEdge', edge.EDGE_TYPE, "invalid edge type for 7. edge")
            self.assertEqual((0, 0), edge.start)
            self.assertEqual((10, 0), edge.end)

            edge = path.edges[7]
            self.assertEqual('LineEdge', edge.EDGE_TYPE, "invalid edge type for 8. edge")
            self.assertEqual((10, 0), edge.start)
            self.assertEqual((10, 4), edge.end)

    def test_add_edge_path(self):
        with self.hatch.edit_boundary() as editor:
            path = editor.add_edge_path()
            self.assertEqual('EdgePath', path.PATH_TYPE, "created wrong path type")
            path.add_line((0, 0), (10, 0))
            path.add_arc((10, 5), radius=5, start_angle=270, end_angle=450, is_counter_clockwise=1)
            path.add_ellipse((5, 10), major_axis_vector=(5, 0), minor_axis_length=0.2, start_angle=0, end_angle=180)
            path.add_line((10, 0), (0, 0))
        # exit with statement and create DXF tags

        with self.hatch.edit_boundary() as editor:
            path = editor.paths[-1]
            edge = path.edges[0]
            self.assertEqual('LineEdge', edge.EDGE_TYPE, "invalid edge type for 1. edge")
            self.assertEqual((0, 0), edge.start)
            self.assertEqual((10, 0), edge.end)

            edge = path.edges[1]
            self.assertEqual('ArcEdge', edge.EDGE_TYPE, "invalid edge type for 2. edge")
            self.assertEqual((10, 5), edge.center)
            self.assertEqual(5, edge.radius)
            self.assertEqual(270, edge.start_angle)
            self.assertEqual(450, edge.end_angle)
            self.assertTrue(edge.is_counter_clockwise)

            edge = path.edges[2]
            self.assertEqual('EllipseEdge', edge.EDGE_TYPE, "invalid edge type for 3. edge")
            self.assertEqual((5, 10), edge.center)
            self.assertEqual((5, 0), edge.major_axis_vector)
            self.assertEqual(.2, edge.minor_axis_length)
            self.assertEqual(0, edge.start_angle)
            self.assertEqual(180, edge.end_angle)
            self.assertFalse(edge.is_counter_clockwise)

            edge = path.edges[3]
            self.assertEqual('LineEdge', edge.EDGE_TYPE, "invalid edge type for 4. edge")
            self.assertEqual((10, 0), edge.start)
            self.assertEqual((0, 0), edge.end)

class TestEdgeHatchWithSpline(unittest.TestCase):
    def setUp(self):
        tags = ClassifiedTags.from_text(EDGE_HATCH_WITH_SPLINE)
        self.hatch = Hatch(tags)

    def test_get_params(self):
        with self.hatch.edit_boundary() as editor:
            path = editor.paths[0]
            spline = None
            for edge in path.edges:
                if edge.EDGE_TYPE == "SplineEdge":
                    spline = edge
                    break
            self.assertIsNotNone(spline, "Spline edge not found.")
            self.assertEqual(3, spline.degree)
            self.assertEqual(0, spline.rational)
            self.assertEqual(0, spline.periodic)
            self.assertEqual((0, 0), spline.start_tangent)
            self.assertEqual((0, 0), spline.end_tangent)
            self.assertEqual(10, len(spline.knot_values))
            self.assertEqual(11.86874452602773, spline.knot_values[-1])
            self.assertEqual(6, len(spline.control_points))
            self.assertEqual((0, 10), spline.control_points[0], "Unexpected start control point.")
            self.assertEqual((0, 0), spline.control_points[-1], "Unexpected end control point.")
            self.assertEqual(0, len(spline.weights))
            self.assertEqual(4, len(spline.fit_points))
            self.assertEqual((0, 10), spline.fit_points[0], "Unexpected start fit point.")
            self.assertEqual((0, 0), spline.fit_points[-1], "Unexpected end fit point.")

    def test_create_spline_edge(self):
        # create the spline
        with self.hatch.edit_boundary() as editor:
            path = editor.paths[0]
            spline = path.add_spline([(1, 1), (2, 2), (3, 3), (4, 4)], degree=3, rational=1, periodic=1)
            # the following values do not represent a mathematically valid spline
            spline.control_points = [(1, 1), (2, 2), (3, 3), (4, 4)]
            spline.knot_values = [1, 2, 3, 4, 5, 6]
            spline.weights = [4, 3, 2, 1]
            spline.start_tangent = (10, 1)
            spline.end_tangent = (2, 20)

        # test the spline
        with self.hatch.edit_boundary() as editor:
            path = editor.paths[0]
            spline = path.edges[-1]
            self.assertEqual(3, spline.degree)
            self.assertEqual(1, spline.rational)
            self.assertEqual(1, spline.periodic)
            self.assertEqual((10, 1), spline.start_tangent)
            self.assertEqual((2, 20), spline.end_tangent)
            self.assertEqual([(1, 1), (2, 2), (3, 3), (4, 4)], spline.control_points)
            self.assertEqual([(1, 1), (2, 2), (3, 3), (4, 4)], spline.fit_points)
            self.assertEqual([1, 2, 3, 4, 5, 6], spline.knot_values)
            self.assertEqual([4, 3, 2, 1], spline.weights)

class TestHatchPatternRead(unittest.TestCase):
    def setUp(self):
        tags = ClassifiedTags.from_text(HATCH_PATTERN)
        self.hatch = Hatch(tags)

    def test_edit_pattern(self):
        with self.hatch.edit_pattern() as pattern_editor:
            self.assertEqual(2, len(pattern_editor.lines))

            line0 = pattern_editor.lines[0]
            self.assertEqual(45, line0.angle)
            self.assertEqual((0, 0), line0.base_point)
            self.assertEqual((-0.1767766952966369, 0.1767766952966369), line0.offset)
            self.assertEqual(0, len(line0.dash_length_items))

            line1 = pattern_editor.lines[1]
            self.assertEqual(45, line1.angle)
            self.assertEqual((0.176776695, 0), line1.base_point)
            self.assertEqual((-0.1767766952966369, 0.1767766952966369), line1.offset)
            self.assertEqual(2, len(line1.dash_length_items))
            self.assertEqual([0.125, -0.0625], line1.dash_length_items)

class TestHatchPatternCreate(unittest.TestCase):
    def setUp(self):
        tags = ClassifiedTags.from_text(_HATCH_TPL)
        self.hatch = Hatch(tags)

    def test_create_new_hatch(self):
        pattern = [
            [45, (0, 0), (0, 1), []],  # 1. Line: continuous
            [45, (0, 0.5), (0, 1), [0.2, -0.1]]  # 2. Line: dashed
        ]
        self.hatch.set_pattern_fill("MOZMAN", definition=pattern)

        self.assertEqual("MOZMAN", self.hatch.dxf.pattern_name)
        with self.hatch.edit_pattern() as p:
            line0 = p.lines[0]
            self.assertEqual(45, line0.angle)
            self.assertEqual((0, 0), line0.base_point)
            self.assertEqual((0, 1), line0.offset)
            self.assertEqual(0, len(line0.dash_length_items))

            line1 = p.lines[1]
            self.assertEqual(45, line1.angle)
            self.assertEqual((0, 0.5), line1.base_point)
            self.assertEqual((0, 1), line1.offset)
            self.assertEqual(2, len(line1.dash_length_items))
            self.assertEqual([0.2, -0.1], line1.dash_length_items)

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

HATCH_PATTERN = """0
HATCH
  5
1EA
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
ANSI33
 70
     0
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
 52
0.0
 41
1.0
 77
     0
 78
     2
 53
45.0
 43
0.0
 44
0.0
 45
-0.1767766952966369
 46
0.1767766952966369
 79
     0
 53
45.0
 43
0.176776695
 44
0.0
 45
-0.1767766952966369
 46
0.1767766952966369
 79
     2
 49
0.125
 49
-0.0625
 47
0.0180224512632811
 98
        1
 10
3.5
 20
6.0
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