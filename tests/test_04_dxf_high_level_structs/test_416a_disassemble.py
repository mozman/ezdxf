#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import Vec3
from ezdxf import disassemble
from ezdxf.entities import factory


def test_do_nothing():
    assert list(disassemble.recursive_decompose([])) == []
    assert list(disassemble.to_primitives([])) == []
    assert list(disassemble.to_vertices([])) == []


def test_convert_unsupported_entity_to_primitive():
    p = disassemble.make_primitive(factory.new('3DSOLID'))
    assert p.path is None
    assert p.mesh is None
    assert p.is_empty is True
    assert list(p.vertices()) == []


def test_multiple_unsupported_entities_to_vertices():
    w = factory.new('3DSOLID')
    primitives = list(disassemble.to_primitives([w, w, w]))
    assert len(primitives) == 3, "3 empty primitives expected"
    vertices = list(disassemble.to_vertices(primitives))
    assert len(vertices) == 0, "no vertices expected"


def test_point_to_primitive():
    e = factory.new('POINT', dxfattribs={'location': (1, 2, 3)})
    p = disassemble.make_primitive(e)
    assert p.is_empty is False
    assert p.path is not None
    assert p.mesh is None
    assert list(p.vertices()) == [(1, 2, 3)]


def test_line_to_primitive():
    start = Vec3(1, 2, 3)
    end = Vec3(4, 5, 6)
    e = factory.new('LINE', dxfattribs={'start': start, 'end': end})
    p = disassemble.make_primitive(e)
    assert p.is_empty is False
    assert p.path is not None
    assert p.mesh is None
    assert list(p.vertices()) == [start, end]


def test_lwpolyline_to_primitive():
    p1 = Vec3(1, 1)
    p2 = Vec3(2, 2)
    p3 = Vec3(3, 3)
    e = factory.new('LWPOLYLINE')
    e.append_points([p1, p2, p3], format="xy")
    p = disassemble.make_primitive(e)
    assert p.is_empty is False
    assert p.path is not None
    assert p.mesh is None
    assert list(p.vertices()) == [p1, p2, p3]


def test_circle_to_primitive():
    e = factory.new('CIRCLE', dxfattribs={'radius': 5})
    p = disassemble.make_primitive(e)
    assert p.is_empty is False
    assert p.path is not None
    assert p.mesh is None
    assert len(list(p.vertices())) > 32


def test_arc_to_primitive():
    e = factory.new('ARC', dxfattribs={'radius': 5})
    p = disassemble.make_primitive(e)
    assert p.is_empty is False
    assert p.path is not None
    assert p.mesh is None
    assert len(list(p.vertices())) > 32


def test_ellipse_to_primitive():
    e = factory.new('ELLIPSE', dxfattribs={'major_axis': (5, 0)})
    p = disassemble.make_primitive(e)
    assert p.is_empty is False
    assert p.path is not None
    assert p.mesh is None
    assert len(list(p.vertices())) > 32


def test_spline_to_primitive():
    e = factory.new('SPLINE')
    e.control_points = [(0, 0), (3, 2), (6, -2), (9, 4)]
    p = disassemble.make_primitive(e)
    assert p.is_empty is False
    assert p.path is not None
    assert p.mesh is None
    assert len(list(p.vertices())) > 20
    assert len(list(p.path.flattening(0.01))) > 20


def test_mesh_entity_to_primitive():
    from ezdxf.layouts import VirtualLayout
    from ezdxf.render.forms import cube
    vl = VirtualLayout()
    mesh_entity = cube().render_mesh(vl)
    assert mesh_entity.dxftype() == "MESH"

    p = disassemble.make_primitive(mesh_entity)
    assert p.is_empty is False
    assert p.path is None
    mesh_builder = p.mesh
    assert mesh_builder is not None
    assert p.is_empty is False

    assert len(mesh_builder.vertices) == 8
    assert len(mesh_builder.faces) == 6
    assert len(list(p.vertices())) == 8


@pytest.mark.parametrize('dxftype', ['SOLID', 'TRACE', '3DFACE'])
def test_from_quadrilateral_with_3_points(dxftype):
    entity = factory.new(dxftype)
    entity.dxf.vtx0 = (0, 0, 0)
    entity.dxf.vtx1 = (1, 0, 0)
    entity.dxf.vtx2 = (1, 1, 0)
    entity.dxf.vtx3 = (1, 1, 0)  # last point is repeated
    p = disassemble.make_primitive(entity)
    assert p.is_empty is False
    assert p.path is not None
    assert p.mesh is None
    assert len(list(p.vertices())) == 4, "expected closed path"


@pytest.mark.parametrize('dxftype', ['SOLID', 'TRACE', '3DFACE'])
def test_from_quadrilateral_with_4_points(dxftype):
    entity = factory.new(dxftype)
    entity.dxf.vtx0 = (0, 0, 0)
    entity.dxf.vtx1 = (1, 0, 0)
    entity.dxf.vtx2 = (1, 1, 0)
    entity.dxf.vtx3 = (0, 1, 0)
    p = disassemble.make_primitive(entity)
    assert p.is_empty is False
    assert p.path is not None
    assert p.mesh is None
    assert len(list(p.vertices())) == 5, "expected closed path"


def test_poly_face_mesh_to_primitive():
    from ezdxf.layouts import VirtualLayout
    from ezdxf.render.forms import cube
    vl = VirtualLayout()
    poly_face_mesh = cube().render_polyface(vl)
    assert poly_face_mesh.dxftype() == "POLYLINE"

    p = disassemble.make_primitive(poly_face_mesh)
    assert p.is_empty is False
    assert p.path is None
    mesh_builder = p.mesh
    assert mesh_builder is not None

    assert len(mesh_builder.vertices) == 8
    assert len(mesh_builder.faces) == 6
    assert len(list(p.vertices())) == 8


def test_poly_mesh_to_primitive():
    from ezdxf.layouts import VirtualLayout
    vl = VirtualLayout()
    poly_mesh = vl.add_polymesh(size=(4, 4))
    for x in range(4):
        for y in range(4):
            poly_mesh.set_mesh_vertex((x, y), (x, y, 1.0))

    p = disassemble.make_primitive(poly_mesh)
    assert p.is_empty is False
    assert p.path is None
    mesh_builder = p.mesh
    assert mesh_builder is not None

    assert len(mesh_builder.vertices) == 16
    assert len(mesh_builder.faces) == 9
    assert len(list(p.vertices())) == 16


def test_2d_3d_polyline_to_primitive():
    from ezdxf.layouts import VirtualLayout
    vl = VirtualLayout()

    p1 = Vec3(1, 1)
    p2 = Vec3(2, 2)
    p3 = Vec3(3, 3)
    e2d = vl.add_polyline2d([p1, p2, p3])
    e3d = vl.add_polyline3d([p1, p2, p3])
    for e in [e2d, e3d]:
        p = disassemble.make_primitive(e)
        assert p.is_empty is False
        assert p.path is not None
        assert p.mesh is None
        assert list(p.vertices()) == [p1, p2, p3]


def test_text_to_primitive():
    # Testing just the control flow, correct bounding boxes are visually tested.
    # see: ezdxf/examples/entities/text.py
    text = factory.new('TEXT')
    text.dxf.text = "0123456789"
    p = disassemble.make_primitive(text)
    assert p.is_empty is False
    assert p.path is not None
    assert p.mesh is None
    assert len(list(p.vertices())) == 5, "expected closed box"


def test_mtext_to_primitive():
    # Testing just the control flow, correct bounding boxes are visually tested.
    # see: ezdxf/examples/entities/mtext.py
    mtext = factory.new('MTEXT')
    mtext.text = "0123456789"
    p = disassemble.make_primitive(mtext)
    assert p.is_empty is False
    assert p.path is not None
    assert p.mesh is None
    assert len(list(p.vertices())) == 5, "expected closed box"


def test_make_primitive_for_hatch_is_empty():
    hatch = factory.new('HATCH')
    # make_primitive() returns an empty primitive, because a HATCH entity can
    # not be reduced into a single path or mesh.
    prim = disassemble.make_primitive(hatch)
    assert prim.is_empty


def test_hatch_returns_multiple_primitives():
    hatch = factory.new('HATCH')
    paths = hatch.paths

    # Conversion of boundary paths is tested in 708.
    paths.add_polyline_path([(0, 0), (1, 0), (1, 1)])
    paths.add_polyline_path([(0, 2), (1, 2), (1, 3), (0, 3)])
    res = list(disassemble.to_primitives([hatch]))
    assert len(res) == 2
    p0 = res[0]
    p1 = res[1]
    assert p0.path is not None
    assert p1.path is not None
    v0 = list(p0.vertices())
    v1 = list(p1.vertices())
    assert len(v0) == 4, "expected closed triangle"
    assert len(v1) == 5, "expected closed box"


def test_image_primitive():
    image = factory.new('IMAGE')
    image.dxf.insert = (0, 0)
    image.dxf.u_pixel = Vec3(1, 0)
    image.dxf.v_pixel = Vec3(0, -1)
    image.size = (200, 100)
    image.boundary_path = [(0, 0), (200, 100)]
    prim = disassemble.make_primitive(image)
    vertices = list(prim.vertices())
    assert len(vertices) == 5, "expected closed box"
    assert vertices[0] == (0.5, -0.5, 0)
    assert vertices[1] == (200.5, -0.5, 0)
    assert vertices[2] == (200.5, 99.5, 0)
    assert vertices[3] == (0.5, 99.5, 0)


@pytest.fixture(scope='module')
def circle_primitive():
    circle = factory.new('CIRCLE', dxfattribs={'radius': 3})
    return disassemble.make_primitive(circle)


def test_to_vertices(circle_primitive):
    vertices = list(disassemble.to_vertices([circle_primitive]))
    assert len(vertices) == 40


def test_to_control_vertices(circle_primitive):
    vertices = list(disassemble.to_control_vertices([circle_primitive]))
    # control points from 4 cubic bezier curves:
    assert len(vertices) == 13  # closed: first == last


if __name__ == '__main__':
    pytest.main([__file__])
