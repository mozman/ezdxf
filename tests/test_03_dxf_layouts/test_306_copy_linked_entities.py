# Created: 12.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new2()


def test_duplicate_simple_entity(doc):
    msp = doc.modelspace()
    circle = msp.add_circle(center=(2, 3), radius=1.5, dxfattribs={'layer': 'test', 'color': 4})
    new_circle = circle.copy()
    assert circle.dxf.handle != new_circle.dxf.handle, "expected new handle"
    assert new_circle.dxf.center == (2, 3)
    assert new_circle.dxf.radius == 1.5
    assert new_circle.dxf.layer == 'test'
    assert new_circle.dxf.color == 4
    assert new_circle.dxf.owner is None  # undefined owner/layout
    with pytest.raises(ezdxf.DXFKeyError):
        doc.layouts.get_layout_for_entity(new_circle)


def test_duplicate_polyline_entity(doc):
    msp = doc.modelspace()
    polyline = msp.add_polyline3d(points=[(1, 1, 1), (3, 2, -1), (7, 4, 4)], dxfattribs={'layer': 'test', 'color': 4})
    start_len = len(doc.entitydb)
    new_polyline = polyline.copy()
    assert len(doc.entitydb) == start_len+4  # POLYLINE, 3x VERTEX, no SEQEND
    assert polyline.dxf.handle != new_polyline.dxf.handle, "expected new handle"
    assert new_polyline.dxf.layer == 'test'
    assert new_polyline.dxf.color == 4
    assert new_polyline.dxf.owner is None  # undefined owner/layout

    assert len(polyline.vertices) == len(new_polyline.vertices)
    for v1, v2 in zip(polyline.vertices, new_polyline.vertices):
        assert v1.dxf.handle != v2.dxf.handle, "expected new handle"
        assert v1.dxf.location == v2.dxf.location


def test_duplicate_insert_with_attribs_entity(doc):
    msp = doc.modelspace()
    insert = msp.add_blockref(name='', insert=(3, 4))
    insert.add_attrib('TAG1', 'content1', insert=(5, 6))
    insert.add_attrib('TAG2', 'content2', insert=(6, 6))
    start_len = len(doc.entitydb)
    new_insert = insert.copy()
    assert len(doc.entitydb) == start_len+3  # INSERT, 2x ATTRIB, no SEQEND
    assert insert.dxf.handle != new_insert.dxf.handle, "expected new handle"

    assert new_insert.dxf.owner is None  # undefined owner/layout

    assert len(insert.attribs) == len(new_insert.attribs)
    for a1, a2 in zip(insert.attribs, new_insert.attribs):
        assert a1.dxf.handle != a2.dxf.handle, "expected new handle"
        assert a1.dxf.tag == a2.dxf.tag
        assert a1.dxf.text == a2.dxf.text
