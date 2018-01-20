# Created: 2011-05-01, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
import ezdxf
from ezdxf.tools import test


@pytest.fixture(scope='module')
def layout():
    dwg = ezdxf.new('AC1015')
    return dwg.modelspace()


def test_new_line(layout):
    points = [(1, 1), (2, 2), (3, 3)]
    line = layout.add_lwpolyline(points)
    assert points == list(line.get_rstrip_points())
    assert 3 == len(line)
    assert line.closed is False , "Polyline should be open by default."


def test_getitem_first(layout):
    points = [(1, 1), (2, 2), (3, 3)]
    line = layout.add_lwpolyline(points)
    assert (1, 1, 0, 0, 0) == line[0]


def test_getitem_last(layout):
    points = [(1, 1), (2, 2), (3, 3)]
    line = layout.add_lwpolyline(points)
    assert (3, 3, 0, 0, 0) == line[-1]


def test_getitem_error(layout):
    points = [(1, 1), (2, 2), (3, 3)]
    line = layout.add_lwpolyline(points)
    with pytest.raises(ezdxf.DXFIndexError):
        line[3]


def test_append_points(layout):
    points = [(1, 1), (2, 2), (3, 3)]
    line = layout.add_lwpolyline(points)
    line.append_points([(4, 4), (5, 5)])
    assert (4, 4, 0, 0, 0) == line[-2]


def test_context_manager(layout):
    points = [(1, 1), (2, 2), (3, 3)]
    line = layout.add_lwpolyline(points)
    with line.points() as p:
        p.extend([(4, 4), (5, 5)])
    assert (4, 4, 0, 0, 0) == line[-2]


def test_discard_points(layout):
    points = [(1, 1), (2, 2), (3, 3)]
    line = layout.add_lwpolyline(points, {'closed': True})
    assert line.closed is True, "Polyline should be closed"
    line.discard_points()
    assert 0 == len(line), "Polyline count should be 0."
    assert len(list(line.get_points())) == 0, "Polyline should not have any points."
    assert line.closed is True, "Polyline should be closed"


def test_delete_const_width(layout):
    points = [(1, 1), (2, 2), (3, 3)]
    line = layout.add_lwpolyline(points)
    line.dxf.const_width = 0.1
    assert 0.1 == pytest.approx(line.dxf.const_width)
    del line.dxf.const_width
    assert line.AcDbPolyline.has_tag(43) is False


def test_rstrip_points(layout):
    points = [(0, 0), (2, 2), (3, 3)]
    line = layout.add_lwpolyline(points)
    rpoints = list(line.get_rstrip_points())
    assert rpoints[0] == (0, 0)


@pytest.fixture
def lwpolyline(layout):
    tags = test.ExtendedTags.from_text(LWPOLYLINE1)
    return layout._dxffactory.wrap_entity(tags)


def test_handle(lwpolyline):
    assert '239' == lwpolyline.dxf.handle
    assert 2 == lwpolyline.dxf.count
    lwpolyline.append_points([(10, 12), (13, 13)])
    assert 4 == len(list(lwpolyline))
    assert 4 == lwpolyline.dxf.count


LWPOLYLINE1 = """  0
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
