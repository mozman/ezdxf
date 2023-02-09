# Copyright (c) 2011-2020, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.lldxf.const import VTX_3D_POLYLINE_VERTEX
from ezdxf import DXFIndexError
from ezdxf.layouts import VirtualLayout


@pytest.fixture
def msp():
    return VirtualLayout()


def test_create_polyline2D(msp):
    polyline = msp.add_polyline2d([(0, 0), (1, 1)])
    assert (0.0, 0.0) == polyline[0].dxf.location
    assert (1.0, 1.0) == polyline[1].dxf.location
    assert "AcDb2dPolyline" == polyline.get_mode()


def test_create_polyline3D(msp):
    polyline = msp.add_polyline3d([(1, 2, 3), (4, 5, 6)])
    assert (1.0, 2.0, 3.0) == polyline[0].dxf.location
    assert (4.0, 5.0, 6.0) == polyline[1].dxf.location
    assert VTX_3D_POLYLINE_VERTEX == polyline[0].dxf.flags
    assert "AcDb3dPolyline" == polyline.get_mode()


def test_polyline3d_vertex_layer(msp):
    attribs = {"layer": "polyline_layer"}
    polyline = msp.add_polyline3d([(1, 2, 3), (4, 5, 6)], dxfattribs=attribs)
    for vertex in polyline.vertices:
        assert (
            "polyline_layer" == vertex.dxf.layer
        ), "VERTEX entity not on the same layer as the POLYLINE entity."


def test_polyline3d_change_polyline_layer(msp):
    attribs = {"layer": "polyline_layer"}
    polyline = msp.add_polyline3d([(1, 2, 3), (4, 5, 6)], dxfattribs=attribs)
    polyline.dxf.layer = "changed_layer"
    for vertex in polyline.vertices:
        assert (
            "changed_layer" == vertex.dxf.layer
        ), "VERTEX entity not on the same layer as the POLYLINE entity."


def test_polyline2d_set_vertex(msp):
    polyline = msp.add_polyline2d([(0, 0), (1, 1), (2, 2), (3, 3)])
    polyline[2].dxf.location = (7, 7)
    assert (7.0, 7.0) == polyline[2].dxf.location


def test_polyline2d_points(msp):
    points = [(0, 0), (1, 1), (2, 2), (3, 3)]
    polyline = msp.add_polyline2d(points)
    assert points == list(polyline.points())


def test_polyline2d_point_slicing(msp):
    points = [(0, 0), (1, 1), (2, 2), (3, 3)]
    polyline = msp.add_polyline2d(points)
    assert [(1, 1), (2, 2)] == list(polyline.points())[1:3]


def test_poyline2d_append_vertices(msp):
    polyline = msp.add_polyline2d([(0, 0), (1, 1)])
    polyline.append_vertices([(7, 7), (8, 8)])
    assert (7.0, 7.0) == polyline[2].dxf.location
    assert 4 == len(polyline)


def test_polyline2d_insert_vertices(msp):
    polyline = msp.add_polyline2d([(0, 0), (1, 1)])
    polyline.insert_vertices(0, [(7, 7), (8, 8)])
    assert (7, 7) == polyline[0].dxf.location
    assert (1, 1) == polyline[3].dxf.location
    assert 4 == len(polyline)


def test_polyline2d_delete_one_vertex(msp):
    polyline = msp.add_polyline2d([(0, 0), (1, 1), (2, 2), (3, 3)])
    del polyline.vertices[0]
    assert (1, 1) == polyline[0].dxf.location
    assert 3 == len(polyline)


def test_polyline2d_delete_two_vertices(msp):
    polyline = msp.add_polyline2d([(0, 0), (1, 1), (2, 2), (3, 3)])
    del polyline.vertices[0:2]
    assert (2, 2) == polyline[0].dxf.location
    assert 2 == len(polyline)


def test_polymesh_create_mesh(msp):
    msp.add_polymesh((4, 4))
    assert True


def test_polymesh_set_vertex(msp):
    mesh = msp.add_polymesh((4, 4))
    mesh.set_mesh_vertex((1, 1), (1, 2, 3))
    result = mesh.get_mesh_vertex((1, 1)).dxf.location
    assert (1, 2, 3) == result


def test_polymesh_error_nindex(msp):
    mesh = msp.add_polymesh((4, 4))
    with pytest.raises(DXFIndexError):
        mesh.get_mesh_vertex((0, 4))


def test_polymesh_error_mindex(msp):
    mesh = msp.add_polymesh((4, 4))
    with pytest.raises(DXFIndexError):
        mesh.get_mesh_vertex((4, 0))


def test_polymesh_mesh_cache(msp):
    pos = (2, 1)
    mesh = msp.add_polymesh((4, 4))
    cache = mesh.get_mesh_vertex_cache()
    cache[pos] = (1, 2, 3)
    vertex = mesh.get_mesh_vertex(pos)
    assert vertex.dxf.location == cache[pos]
    with pytest.raises(DXFIndexError):
        cache[4, 0]


def test_polyface_create_face(msp):
    face = msp.add_polyface()
    assert 0 == len(face)


def test_polyface_add_face(msp):
    face = msp.add_polyface()
    face.append_face([(0, 0), (1, 1), (2, 2), (3, 3)])
    assert [(0, 0), (1, 1), (2, 2), (3, 3), (0, 0, 0)] == list(face.points())


def test_polyface_face_indices(msp):
    face = msp.add_polyface()
    face.append_face([(0, 0), (1, 1), (2, 2), (3, 3)])
    face_record = face[4]
    assert 1 == face_record.dxf.vtx0
    assert 2 == face_record.dxf.vtx1
    assert 3 == face_record.dxf.vtx2
    assert 4 == face_record.dxf.vtx3


def test_polyface_add_two_face_indices(msp):
    face = msp.add_polyface()
    face.append_face([(0, 0), (1, 1), (2, 2), (3, 3)])
    # second face has same vertices as the first face
    face.append_face([(0, 0), (1, 1), (2, 2)])
    face_record = face[5]  # second face
    assert 1 == face_record.dxf.vtx0
    assert 2 == face_record.dxf.vtx1
    assert 3 == face_record.dxf.vtx2
    assert 4 == face.dxf.m_count  # vertices count
    assert 2 == face.dxf.n_count  # faces count


def test_polyface_faces(msp):
    face = msp.add_polyface()
    face.append_face([(0, 0), (1, 1), (2, 2), (3, 3)])
    face.append_face([(0, 0), (1, 1), (2, 2)])
    result = list(face.faces())
    assert 2 == len(result)
    points1 = [vertex.dxf.location for vertex in result[0]]
    # the last vertex is the face_record and is always (0, 0, 0)
    # the face_record contains indices to the face building vertices
    assert [(0, 0, 0), (1, 1, 0), (2, 2, 0), (3, 3, 0), (0, 0, 0)] == points1


def test_polyface_optimized_cube(msp):
    face = msp.add_polyface()
    # a cube consist of 6 faces and 24 vertices
    # duplicated vertices should be removed
    face.append_faces(cube_faces())
    assert 8 == face.dxf.m_count  # vertices count
    assert 6 == face.dxf.n_count  # faces count


def cube_faces():
    # cube corner points
    p1 = (0, 0, 0)
    p2 = (0, 0, 1)
    p3 = (0, 1, 0)
    p4 = (0, 1, 1)
    p5 = (1, 0, 0)
    p6 = (1, 0, 1)
    p7 = (1, 1, 0)
    p8 = (1, 1, 1)

    # define the 6 cube faces
    # look into -x direction
    # Every add_face adds 4 vertices 6x4 = 24 vertices
    return [
        [p1, p5, p7, p3],
        [p1, p5, p6, p2],
        [p5, p7, p8, p6],
        [p7, p8, p4, p3],
        [p1, p3, p4, p2],
        [p2, p6, p8, p4],
    ]
