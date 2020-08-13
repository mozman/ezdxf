# Created: 25.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.entities.dxfgfx import DXFGraphic


@pytest.fixture(scope='module')
def msp():
    doc = ezdxf.new()
    return doc.modelspace()


def test_delete_polyline3d(msp):
    entity_count = len(msp)
    db = msp.entitydb
    db_count = len(db)
    pline = msp.add_polyline3d([(0, 0, 0), (1, 2, 3), (4, 5, 6)])
    assert entity_count + 1 == len(
        msp), 'vertices should be linked to the POLYLINE entity'
    assert db_count + 5 == len(
        msp.entitydb), 'database should get 4 vertices and 1 seqend'

    assert pline.seqend.dxf.owner == pline.dxf.owner
    assert pline.seqend.dxf.handle is not None
    assert pline.seqend.dxf.handle in msp.doc.entitydb

    assert len(pline) == 3
    assert pline.vertices[0].dxf.location == (0, 0, 0)
    assert pline.vertices[1].dxf.location == (1, 2, 3)
    assert pline.vertices[2].dxf.location == (4, 5, 6)
    assert pline.get_mode() == 'AcDb3dPolyline'
    assert pline.is_3d_polyline is True
    assert pline.is_2d_polyline is False
    assert pline.is_closed is False
    assert list(pline.points()) == [(0, 0, 0), (1, 2, 3), (4, 5, 6)]
    msp.delete_entity(pline)
    assert entity_count == len(msp)

    db.purge()
    assert len(db) == db_count


def test_create_line(msp):
    line = msp.add_line((0, 0), (1, 1))
    assert line.dxf.start == (0., 0.)
    assert line.dxf.end == (1., 1.)


def test_create_point(msp):
    point = msp.add_point((1, 2))
    assert point.dxf.location == (1, 2)


def test_create_circle(msp):
    circle = msp.add_circle((3, 3), 5)
    assert circle.dxf.center == (3., 3.)
    assert circle.dxf.radius == 5.


def test_create_arc(msp):
    arc = msp.add_arc((3, 3), 5, 30, 60)
    assert arc.dxf.center == (3., 3.)
    assert arc.dxf.radius == 5.
    assert arc.dxf.start_angle == 30.
    assert arc.dxf.end_angle == 60.


def test_create_trace(msp):
    trace = msp.add_trace([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert trace[0] == (0, 0)
    assert trace.dxf.vtx1 == (1, 0)
    assert trace[2] == (1, 1)
    assert trace.dxf.vtx3 == (0, 1)


def test_create_solid(msp):
    trace = msp.add_solid([(0, 0), (1, 0), (1, 1)])
    assert trace.dxf.vtx0 == (0, 0)
    assert trace[1] == (1, 0)
    assert trace.dxf.vtx2 == (1, 1)
    assert trace[3] == (1, 1)


def test_create_3dface(msp):
    trace = msp.add_3dface([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)])
    assert trace.dxf.vtx0 == (0, 0, 0)
    assert trace[1] == (1, 0, 0)
    assert trace.dxf.vtx2 == (1, 1, 0)
    assert trace[3] == (0, 1, 0)


def test_create_text(msp):
    text = msp.add_text('text')
    assert text.dxf.text == 'text'


def test_create_shape(msp):
    shape = msp.add_shape("TestShape", (1, 2), 3.0)
    assert shape.dxf.name == "TestShape"
    assert shape.dxf.insert == (1.0, 2.0)
    assert shape.dxf.size == 3
    assert shape.dxf.rotation == 0
    assert shape.dxf.xscale == 1
    assert shape.dxf.oblique == 0


class Checker(DXFGraphic):
    def post_bind_hook(self) -> None:
        self._post_bind_hook = True


def test_post_bind_hook_call(msp):
    checker = Checker()
    checker.doc = msp.doc
    msp.add_entity(checker)
    assert checker._post_bind_hook is True
