# Created: 12.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
import ezdxf


@pytest.fixture(params=['R12', 'R2000'], scope='module')
def dwg(request):
    return ezdxf.new(request.param)


def test_duplicate_simple_entity(dwg):
    msp = dwg.modelspace()
    circle = msp.add_circle(center=(2, 3), radius=1.5, dxfattribs={'layer': 'test', 'color': 4})
    new_circle = circle.copy()
    assert circle.dxf.handle != new_circle.dxf.handle, "expected new handle"
    assert new_circle.dxf.center == (2, 3)
    assert new_circle.dxf.radius == 1.5
    assert new_circle.dxf.layer == 'test'
    assert new_circle.dxf.color == 4
    if dwg.dxfversion > 'AC1009':  # DXF R2000+
        assert new_circle.dxf.owner == '0'  # undefined owner/layout


def test_duplicate_polyline_entity(dwg):
    msp = dwg.modelspace()
    polyline = msp.add_polyline3d(points=[(1, 1, 1), (3, 2, -1), (7, 4, 4)], dxfattribs={'layer': 'test', 'color': 4})
    start_len = len(dwg.entitydb)
    new_polyline = polyline.copy()
    assert len(dwg.entitydb) == start_len+5  # POLYLINE, 3x VERTEX, 1x SEQEND
    assert polyline.dxf.handle != new_polyline.dxf.handle, "expected new handle"
    assert new_polyline.dxf.layer == 'test'
    assert new_polyline.dxf.color == 4
    if dwg.dxfversion > 'AC1009':  # DXF R2000+
        assert new_polyline.dxf.owner == '0'  # undefined owner/layout

    source_vertices = list(polyline.vertices())
    copy_vertices = list(new_polyline.vertices())
    assert len(source_vertices) == len(copy_vertices)
    for v1, v2 in zip(copy_vertices, source_vertices):
        assert v1.dxf.handle != v2.dxf.handle, "expected new handle"
        assert v1.dxf.location == v2.dxf.location


def test_duplicate_insert_with_attribs_entity(dwg):
    msp = dwg.modelspace()
    insert = msp.add_blockref(name='', insert=(3, 4))
    insert.add_attrib('TAG1', 'content1', insert=(5, 6))
    insert.add_attrib('TAG2', 'content2', insert=(6, 6))
    start_len = len(dwg.entitydb)
    new_insert = insert.copy()
    assert len(dwg.entitydb) == start_len+4  # INSERT, 2x ATTRIB, 1x SEQEND
    assert insert.dxf.handle != new_insert.dxf.handle, "expected new handle"

    if dwg.dxfversion > 'AC1009':  # DXF R2000+
        assert new_insert.dxf.owner == '0'  # undefined owner/layout

    source_attribs = list(insert.attribs())
    copy_attribs = list(new_insert.attribs())
    assert len(source_attribs) == len(copy_attribs)
    for a1, a2 in zip(copy_attribs, source_attribs):
        assert a1.dxf.handle != a2.dxf.handle, "expected new handle"
        assert a1.dxf.tag == a2.dxf.tag
        assert a1.dxf.text == a2.dxf.text
