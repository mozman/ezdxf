# Copyright (C) 2011-2020, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.entities.lwpolyline import format_point, compile_array, LWPolylinePoints, LWPolyline
from ezdxf.math import Vec3


def lwpolyline(points, dxfattribs=None):
    line = LWPolyline.new(dxfattribs=dxfattribs)
    line.set_points(points)
    return line


def lwtags(text):
    tags = ExtendedTags.from_text(text)
    return tags.get_subclass('AcDbPolyline')


def test_new_line():
    points = [(1, 1), (2, 2), (3, 3)]
    line = lwpolyline(points)

    assert points == list(line.vertices())
    assert 3 == len(line)

    assert line.closed is False, "Polyline should be open by default."
    # test callback DXF attribute
    assert 3 == line.dxf.count  # DXF attrib callback
    with pytest.raises(ezdxf.DXFAttributeError):
        line.dxf.count = 0  # set dxf tag 90


def test_get_point():
    points = [(1, 1), (2, 2), (3, 3)]
    line = lwpolyline(points)
    assert (1, 1, 0, 0, 0) == line[0]
    assert (3, 3, 0, 0, 0) == line[-1]


def test_slicing():
    points = [(1, 1), (2, 2), (3, 3)]
    line = lwpolyline(points)
    assert len(line[:1]) == 1
    assert len(line[:]) == 3
    assert len(line[:2]) == 2
    assert len(line[:-1]) == 2
    assert len(line[1:-1]) == 1
    result = line[::-1]
    assert len(result) == 3
    assert result[0] == (3, 3, 0, 0, 0)
    assert result[1] == (2, 2, 0, 0, 0)
    assert result[2] == (1, 1, 0, 0, 0)


def test_set_point():
    points = [(1, 1), (2, 2), (3, 3)]
    line = lwpolyline(points)

    line[0] = (4, 4)
    assert (4, 4, 0, 0, 0) == line[0]

    line[-1] = (4, 4)
    assert (4, 4, 0, 0, 0) == line[-1]


def test_get_point_error():
    points = [(1, 1), (2, 2), (3, 3)]
    line = lwpolyline(points)
    with pytest.raises(ezdxf.DXFIndexError):
        line[3]


def test_insert_point():
    points = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]
    line = lwpolyline(points)
    assert len(line) == 5

    line.insert(0, (7, 8))
    assert len(line) == 6
    assert line[0] == (7, 8, 0, 0, 0)
    assert line[1] == (1, 1, 0, 0, 0)
    assert line[-1] == (5, 5, 0, 0, 0)

    line.insert(1, (1, 9, 4), format='bxy')
    assert len(line) == 7
    assert line[0] == (7, 8, 0, 0, 0)
    assert line[1] == (9, 4, 0, 0, 1)
    assert line[2] == (1, 1, 0, 0, 0)
    assert line[-1] == (5, 5, 0, 0, 0)


def test_del_points():
    points = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]
    line = lwpolyline(points)
    assert len(line) == 5

    del line[0]
    assert len(line) == 4
    assert line[0] == (2, 2, 0, 0, 0)
    assert line[-1] == (5, 5, 0, 0, 0)

    del line[:2]
    assert len(line) == 2
    assert line[0] == (4, 4, 0, 0, 0)
    assert line[-1] == (5, 5, 0, 0, 0)


def test_append_points():
    points = [(1, 1), (2, 2), (3, 3)]
    line = lwpolyline(points)
    line.append_points([(4, 4), (5, 5)])
    assert (4, 4, 0, 0, 0) == line[-2]


def test_context_manager():
    points = [(1, 1), (2, 2), (3, 3)]
    line = lwpolyline(points)
    with line.points() as p:
        p.extend([(4, 4), (5, 5)])
    assert (4, 4, 0, 0, 0) == line[-2]


def test_clear():
    points = [(1, 1), (2, 2), (3, 3)]
    line = lwpolyline(points)
    line.closed = True
    assert line.closed is True, "Polyline should be closed"
    line.clear()
    assert 0 == len(line), "Polyline count should be 0."
    assert len(list(line.get_points())) == 0, "Polyline should not have any points."
    assert line.closed is True, "Polyline should be closed"


def test_delete_const_width():
    points = [(1, 1), (2, 2), (3, 3)]
    line = lwpolyline(points)
    line.dxf.const_width = 0.1
    assert 0.1 == pytest.approx(line.dxf.const_width)
    del line.dxf.const_width


def test_vertices():
    points = [(0, 0, 1, 1, 1), (2, 2, 1, 1, 1), (3, 3, 1, 1, 1)]
    line = lwpolyline(points)
    assert list(line.vertices()) == [(0, 0), (2, 2), (3, 3)]


def test_format_point():
    assert format_point((1, 2, 3, 4, 5), 'xy') == (1, 2)
    assert format_point((1, 2, 3, 4, 5), 'bse') == (5, 3, 4)
    assert format_point((1, 2, 3, 4, 5), 'v,b') == ((1, 2), 5)


def test_point_to_array():
    assert tuple(compile_array((1, 2), 'xy')) == (1, 2, 0, 0, 0)
    assert tuple(compile_array((1, 2, 5), 'xyb')) == (1, 2, 0, 0, 5)
    assert tuple(compile_array((1, 2), 'xyseb')) == (1, 2, 0, 0, 0)

    assert tuple(compile_array((1, 2, 5), 'xy')) == (1, 2, 0, 0, 0)
    assert tuple(compile_array((5, (1, 2)), 'b,v')) == (1, 2, 0, 0, 5)
    # mix of x, y, v codes is allowed, but only last is set
    assert tuple(compile_array(((1, 2), 4, 5), 'vxy')) == (4, 5, 0, 0, 0)


def test_packed_points_basics():
    packed_points, _ = LWPolylinePoints.from_tags(lwtags(LWPOLYLINE1))
    assert len(packed_points) == 2
    points = list(packed_points)
    assert len(points) == 2
    assert packed_points[0] == (-.5, -.5, 0, 0, 0)
    assert packed_points[1] == (.5, .5, 0, 0, 0)
    # test negative index
    assert packed_points[-1] == (.5, .5, 0, 0, 0)
    with pytest.raises(IndexError):
        packed_points[-3]
    with pytest.raises(IndexError):
        packed_points[2]


def test_packed_points_advanced():
    packed_points, _ = LWPolylinePoints.from_tags(lwtags(LWPOLYLINE1))
    packed_points.append((5, 5, 1, 2, 3))
    assert len(packed_points) == 3
    assert packed_points[-1] == (5, 5, 1, 2, 3)
    packed_points[0] = (7, 7, 0, 0, 0)
    assert packed_points[0] == (7, 7, 0, 0, 0)
    assert len(packed_points) == 3
    packed_points.clear()
    assert len(packed_points) == 0


def test_packed_points_to_dxf_tags():
    packed_points, _ = LWPolylinePoints.from_tags(lwtags(LWPOLYLINE1))
    tags = list(packed_points.dxftags())
    assert len(tags) == 2  # just the points
    assert tags[0] == (10, (-.5, -.5))
    assert tags[1] == (10, (.5, .5))


def test_packed_points_to_dxf_tags_with_bulge():
    packed_points, _ = LWPolylinePoints.from_tags(lwtags(LWPOLYLINE1))
    packed_points[0] = (-.5, -.5, 0, 0, 1)
    packed_points[1] = (.5, .5, .1, .2, -1)
    tags = list(packed_points.dxftags())
    assert len(tags) == 6
    assert tags[0] == (10, (-.5, -.5))
    assert tags[1] == (42, 1)
    assert tags[2] == (10, (.5, .5))
    assert tags[3] == (40, .1)
    assert tags[4] == (41, .2)
    assert tags[5] == (42, -1)


def test_lwpolyline_transform_interface():
    pline = LWPolyline()
    pline.set_points([(0, 0), (2, 0), (1, 1)], format='xy')
    pline.translate(1, 1, 1)
    vertices = list(pline.vertices())
    assert vertices[0] == (1, 1)
    assert vertices[1] == (3, 1)
    assert vertices[2] == (2, 2)
    assert pline.dxf.elevation == 1
    assert Vec3(0, 0, 1).isclose(pline.dxf.extrusion)


LWPOLYLINE1 = """0
LWPOLYLINE
5
239
330
238
100
AcDbEntity
8
0
6
ByBlock
62
0
100
AcDbPolyline
90
2
70
0
43
0.15
10
-0.5
20
-0.5
10
0.5
20
0.5
"""
