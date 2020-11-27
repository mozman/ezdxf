# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.render.trace import TraceBuilder, LinearTrace, CurvedTrace
from ezdxf.math import BSpline, Vec2


def test_trace_builder_init():
    t = TraceBuilder()
    assert len(t) == 0


def test_add_station_2d():
    t = LinearTrace()
    t.add_station((0, 0), 1, 2)
    assert len(t) == 1
    assert t[0].vertex == (0, 0)
    assert t[0].start_width == 1
    assert t[0].end_width == 2
    t.add_station((1, 0), 1)
    assert len(t) == 2
    assert t[1].vertex == (1, 0)
    assert t[1].start_width == 1
    assert t[1].end_width == 1


def test_add_station_3d():
    # z-axis is ignored
    t = LinearTrace()
    t.add_station((0, 0, 0), 1, 2)
    assert t[0].vertex == (0, 0)


def test_add_spline_segment():
    t = CurvedTrace.from_spline(BSpline.from_fit_points([(1, 0), (3, 1), (5, -1), (6, 0)]), start_width=2, end_width=1,
                                segments=10)
    assert len(t) == 11


def test_square_face():
    t = LinearTrace()
    t.add_station((0, 0), 1, 1)
    t.add_station((1, 0), 0, 0)
    face = list(t.faces())[0]
    assert face[0].isclose(Vec2(0, +0.5))
    assert face[1].isclose(Vec2(0, -0.5))
    assert face[2].isclose(Vec2(1, -0.5))
    assert face[3].isclose(Vec2(1, +0.5))


def test_closed_linear_path():
    t = LinearTrace()
    t.add_station((0, 0), 1, 1)
    t.add_station((1, 0), 1, 1)
    t.add_station((1, 1), 1, 1)
    t.add_station((0, 1), 1, 1)
    t.add_station((0, 0), 1, 1)
    faces = list(t.faces())
    assert len(faces) == 4
    assert faces[0] == (Vec2(0.5, 0.5), Vec2(-0.5, -0.5), Vec2(1.5, -0.5), Vec2(0.5, 0.5))
    assert faces[3] == (Vec2(0.5, 0.5), Vec2(-0.5, 1.5), Vec2(-0.5, -0.5), Vec2(0.5, 0.5))


def test_two_straight_faces():
    t = LinearTrace()
    t.add_station((0, 0), 1, 1)
    t.add_station((2, 0), 1, 1)
    t.add_station((4, 0), 1, 1)
    face1, face2 = list(t.faces())
    assert face1[0].isclose(Vec2(0, +0.5))
    assert face1[1].isclose(Vec2(0, -0.5))
    assert face1[2].isclose(Vec2(2, -0.5))
    assert face1[3].isclose(Vec2(2, +0.5))
    assert face2[0].isclose(Vec2(2, +0.5))
    assert face2[1].isclose(Vec2(2, -0.5))
    assert face2[2].isclose(Vec2(4, -0.5))
    assert face2[3].isclose(Vec2(4, +0.5))


def test_two_angled_faces():
    t = LinearTrace()
    t.add_station((0, 0), 1, 0.5)
    t.add_station((2, 0), 1, 1)
    t.add_station((4, 2), 1, 1)
    face1, face2 = list(t.faces())
    assert face1[0].isclose(Vec2(0, +0.5))
    assert face1[1].isclose(Vec2(0, -0.5))
    assert face1[2].isclose(Vec2(2.5224077499274835, -0.18469903125906456))
    assert face1[3].isclose(Vec2(1.5936828611675133, 0.3007896423540608))
    assert face2[2].isclose(Vec2(4.353553390593274, 1.6464466094067263))
    assert face2[3].isclose(Vec2(3.646446609406726, 2.353553390593274))


def test_linear_trace_polygon():
    t = LinearTrace()
    t.add_station((0, 0), 1, 1)
    t.add_station((2, 0), 1, 1)
    t.add_station((4, 0), 1, 1)
    polygon = t.polygon()
    assert len(polygon) == 6
    assert polygon[0].isclose(Vec2(0, -0.5))
    assert polygon[-1].isclose(Vec2(0, +0.5))


def test_virtual_entities_added_to_entity_database():
    doc = ezdxf.new()
    msp = doc.modelspace()
    t = LinearTrace()
    t.add_station((0, 0), 1, 1)
    t.add_station((1, 0), 0, 0)

    dxfattribs = {'layer': 'TEST'}
    solid = list(t.virtual_entities('SOLID', dxfattribs, doc))[0]
    assert solid.DXFTYPE == 'SOLID'
    assert solid.dxf.layer == 'TEST'
    assert solid.dxf.handle in doc.entitydb
    msp.add_entity(solid)

    trace = list(t.virtual_entities('TRACE', dxfattribs, doc))[0]
    assert trace.DXFTYPE == 'TRACE'
    assert trace.dxf.layer == 'TEST'
    assert trace.dxf.handle in doc.entitydb
    msp.add_entity(trace)

    face = list(t.virtual_entities('3DFACE', dxfattribs, doc))[0]
    assert face.DXFTYPE == '3DFACE'
    assert face.dxf.layer == 'TEST'
    assert face.dxf.handle in doc.entitydb
    msp.add_entity(face)

    assert len(msp) == 3


@pytest.mark.skip('Cython implementation for Vec3 has a precision problem')
def test_issue_191():
    from ezdxf.entities import factory
    e = factory.new(
        'LWPOLYLINE',
        dxfattribs={
            'flags': 1,
        },
    )
    e.set_points([
        (421846.9857097387, -36908.41493252141, 0.0, 50.0, 0.52056705),
        (421846.9857097387, -36908.41493252139, 0.0, 50.0, 0.52056705),
    ])
    trace = TraceBuilder.from_polyline(e, segments=64)
    assert len(trace) == 1
    assert len(list(trace.faces())) == 32


if __name__ == '__main__':
    pytest.main([__file__])
