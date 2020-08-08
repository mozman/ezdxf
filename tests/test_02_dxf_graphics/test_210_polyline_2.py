# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.lldxf.const import VTX_3D_POLYLINE_VERTEX
from ezdxf.lldxf.tagwriter import TagCollector
from ezdxf.tools.test import load_entities
from ezdxf.sections.entities import EntitySection


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2000')


@pytest.fixture(scope='module')
def layout(dwg):
    return dwg.modelspace()


def test_create_polyline2D(layout):
    polyline = layout.add_polyline2d([(0, 0), (1, 1)])
    assert (0., 0.) == polyline[0].dxf.location
    assert (1., 1.) == polyline[1].dxf.location
    assert 'AcDb2dPolyline' == polyline.get_mode()


def test_create_polyline3D(layout):
    polyline = layout.add_polyline3d([(1, 2, 3), (4, 5, 6)])
    assert (1., 2., 3.) == polyline[0].dxf.location
    assert (4., 5., 6.) == polyline[1].dxf.location
    assert VTX_3D_POLYLINE_VERTEX == polyline[0].dxf.flags
    assert 'AcDb3dPolyline' == polyline.get_mode()


def test_vertex_layer(layout):
    attribs = {'layer': 'polyline_layer'}
    polyline = layout.add_polyline3d([(1, 2, 3), (4, 5, 6)], dxfattribs=attribs)
    for vertex in polyline.vertices:
        assert 'polyline_layer' == vertex.dxf.layer, "VERTEX entity not on the same layer as the POLYLINE entity."


def test_change_polyline_layer(layout):
    attribs = {'layer': 'polyline_layer'}
    polyline = layout.add_polyline3d([(1, 2, 3), (4, 5, 6)], dxfattribs=attribs)
    polyline.dxf.layer = "changed_layer"
    for vertex in polyline.vertices:
        assert 'changed_layer' == vertex.dxf.layer, "VERTEX entity not on the same layer as the POLYLINE entity."


def test_set_vertex(layout):
    polyline = layout.add_polyline2d([(0, 0), (1, 1), (2, 2), (3, 3)])
    polyline[2].dxf.location = (7, 7)
    assert (7., 7.) == polyline[2].dxf.location


def test_points(layout):
    points = [(0, 0), (1, 1), (2, 2), (3, 3)]
    polyline = layout.add_polyline2d(points)
    assert points == list(polyline.points())


def test_point_slicing(layout):
    points = [(0, 0), (1, 1), (2, 2), (3, 3)]
    polyline = layout.add_polyline2d(points)
    assert [(1, 1), (2, 2)] == list(polyline.points())[1:3]


def test_append_vertices(layout):
    polyline = layout.add_polyline2d([(0, 0), (1, 1)])
    polyline.append_vertices([(7, 7), (8, 8)])
    assert (7., 7.) == polyline[2].dxf.location
    assert 4 == len(polyline)


def test_insert_vertices(layout):
    polyline = layout.add_polyline2d([(0, 0), (1, 1)])
    polyline.insert_vertices(0, [(7, 7), (8, 8)])
    assert (7, 7) == polyline[0].dxf.location
    assert (1, 1) == polyline[3].dxf.location
    assert 4 == len(polyline)


def test_delete_one_vertex(layout):
    polyline = layout.add_polyline2d([(0, 0), (1, 1), (2, 2), (3, 3)])
    del polyline.vertices[0]
    assert (1, 1) == polyline[0].dxf.location
    assert 3 == len(polyline)


def test_delete_two_vertices(layout):
    polyline = layout.add_polyline2d([(0, 0), (1, 1), (2, 2), (3, 3)])
    del polyline.vertices[0:2]
    assert (2, 2) == polyline[0].dxf.location
    assert 2 == len(polyline)


def test_polymesh_correct_casting(layout):
    mesh1 = layout.add_polymesh((4, 4))
    assert mesh1.dxf.handle is not None
    mesh2 = layout[-1]
    assert mesh1 is mesh2
    assert mesh1.vertices is mesh2.vertices


def test_polymesh_set_vertex(layout):
    mesh = layout.add_polymesh((4, 4))
    mesh.set_mesh_vertex((1, 1), (1, 2, 3))
    assert (1, 2, 3) == mesh.get_mesh_vertex((1, 1)).dxf.location


def test_polymesh_error_n_index(layout):
    mesh = layout.add_polymesh((4, 4))
    with pytest.raises(IndexError):
        mesh.get_mesh_vertex((0, 4))


def test_polymesh_error_m_index(layout):
    mesh = layout.add_polymesh((4, 4))
    with pytest.raises(IndexError):
        mesh.get_mesh_vertex((4, 0))


def test_polymesh_mesh_cache(layout):
    pos = (2, 1)
    mesh = layout.add_polymesh((4, 4))
    cache = mesh.get_mesh_vertex_cache()
    cache[pos] = (1, 2, 3)
    vertex = mesh.get_mesh_vertex(pos)
    assert vertex.dxf.location == cache[pos]
    with pytest.raises(ezdxf.DXFIndexError):
        cache[4, 0]


def test_polyface_correct_casting(layout):
    polyface1 = layout.add_polyface()
    polyface2 = layout[-1]
    assert polyface1 is polyface2
    assert polyface1.vertices is polyface2.vertices


def test_polyface_create_face(layout):
    face = layout.add_polyface()
    assert 0 == len(face)


def test_polyface_add_face(layout):
    face = layout.add_polyface()
    face.append_face([(0, 0), (1, 1), (2, 2), (3, 3)])
    assert [(0, 0), (1, 1) == (2, 2), (3, 3), (0, 0, 0)], list(face.points())


def test_polyface_face_indices(layout):
    face = layout.add_polyface()
    face.append_face([(0, 0), (1, 1), (2, 2), (3, 3)])
    face_record = face[4]
    assert 1 == face_record.dxf.vtx0
    assert 2 == face_record.dxf.vtx1
    assert 3 == face_record.dxf.vtx2
    assert 4 == face_record.dxf.vtx3


def test_polyface_add_two_face_indices(layout):
    face = layout.add_polyface()
    face.append_face([(0, 0), (1, 1), (2, 2), (3, 3)])
    # second face has same vertices as the first face
    face.append_face([(0, 0), (1, 1), (2, 2)])
    face_record = face[5]  # second face
    assert 1 == face_record.dxf.vtx0
    assert 2 == face_record.dxf.vtx1
    assert 3 == face_record.dxf.vtx2
    assert 4 == face.dxf.m_count  # vertices count
    assert 2 == face.dxf.n_count  # faces count


def test_polyface_faces(layout):
    face = layout.add_polyface()
    face.append_face([(0, 0), (1, 1), (2, 2), (3, 3)])
    face.append_face([(0, 0), (1, 1), (2, 2)])
    result = list(face.faces())
    assert 2 == len(result)
    points1 = [vertex.dxf.location for vertex in result[0]]
    # the last vertex is the face_record and is always (0,0,0)
    # the face_record contains indices to the face building vertices
    assert [(0, 0), (1, 1), (2, 2), (3, 3), (0, 0, 0)] == points1


def test_polyface_optimized_cube(layout):
    face = layout.add_polyface()
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


def test_export_polyline2d(layout):
    polyline = layout.add_polyline2d([(0, 0), (1, 1)])
    collector = TagCollector()
    polyline.export_dxf(collector)
    tags = collector.tags
    assert (100, 'AcDb2dPolyline') in tags
    collector.reset()
    polyline[0].export_dxf(collector)
    tags = collector.tags
    assert (100, 'AcDbVertex') in tags
    assert (100, 'AcDb2dVertex') in tags


def test_export_polyline3d(layout):
    polyline = layout.add_polyline3d([(0, 0), (1, 1)])
    collector = TagCollector()
    polyline.export_dxf(collector)
    tags = collector.tags
    assert (100, 'AcDb3dPolyline') in tags
    collector.reset()
    polyline[0].export_dxf(collector)
    tags = collector.tags
    assert (100, 'AcDbVertex') in tags
    assert (100, 'AcDb3dPolylineVertex') in tags


def test_internals_polymesh(layout):
    mesh = layout.add_polymesh((4, 4))
    collector = TagCollector()
    mesh.export_dxf(collector)
    tags = collector.tags
    assert (100, 'AcDbPolygonMesh') in tags
    collector.reset()
    mesh[0].export_dxf(collector)
    tags = collector.tags
    assert (100, 'AcDbVertex') in tags
    assert (100, 'AcDbPolygonMeshVertex') in tags


def test_internals_polyface(layout):
    face = layout.add_polyface()
    face.append_face([(0, 0), (1, 1), (2, 2), (3, 3)])

    collector = TagCollector()
    face.export_dxf(collector)
    tags = collector.tags
    assert (100, 'AcDbPolyFaceMesh') in tags

    collector.reset()
    face[0].export_dxf(collector)
    tags = collector.tags
    assert (100, 'AcDbVertex') in tags
    assert (100, 'AcDbPolyFaceMeshVertex') in tags

    collector.reset()
    face[4].export_dxf(collector)
    tags = collector.tags
    assert (100, 'AcDbVertex') not in tags
    assert (100, 'AcDbFaceRecord') in tags


def test_new_style_polyface_face_count():
    doc = ezdxf.new()
    section = EntitySection(doc, load_entities(NEW_STYLE_POLYFACE, 'ENTITIES'))
    entities = list(section)
    polyface = entities[0]
    faces = list(polyface.faces())
    assert 6 == len(faces)


NEW_STYLE_POLYFACE = """  0
SECTION
  2
ENTITIES
  0
POLYLINE
  5
9A
330
6B
100
AcDbEntity
  8
0
100
AcDbPolyFaceMesh
 66
     1
 10
0.0
 20
0.0
 30
0.0
 70
    64
 71
     8
 72
     6
  0
VERTEX
  5
9B
330
9A
100
AcDbEntity
  8
0
100
AcDbVertex
100
AcDbPolyFaceMeshVertex
 10
0.0
 20
0.0
 30
0.802929163112954
 70
   192
  0
VERTEX
  5
9C
330
9A
100
AcDbEntity
  8
0
100
AcDbVertex
100
AcDbPolyFaceMeshVertex
 10
0.4434395109072581
 20
0.0
 30
0.802929163112954
 70
   192
  0
VERTEX
  5
9D
330
9A
100
AcDbEntity
  8
0
100
AcDbVertex
100
AcDbPolyFaceMeshVertex
 10
0.4434395109072581
 20
0.4434395109072581
 30
0.802929163112954
 70
   192
  0
VERTEX
  5
9E
330
9A
100
AcDbEntity
  8
0
100
AcDbVertex
100
AcDbPolyFaceMeshVertex
 10
0.0
 20
0.4434395109072581
 30
0.802929163112954
 70
   192
  0
VERTEX
  5
9F
330
9A
100
AcDbEntity
  8
0
100
AcDbVertex
100
AcDbPolyFaceMeshVertex
 10
0.4434395109072581
 20
0.0
 30
1.246368674020211
 70
   192
  0
VERTEX
  5
A0
330
9A
100
AcDbEntity
  8
0
100
AcDbVertex
100
AcDbPolyFaceMeshVertex
 10
0.0
 20
0.0
 30
1.246368674020211
 70
   192
  0
VERTEX
  5
A1
330
9A
100
AcDbEntity
  8
0
100
AcDbVertex
100
AcDbPolyFaceMeshVertex
 10
0.4434395109072581
 20
0.4434395109072581
 30
1.246368674020211
 70
   192
  0
VERTEX
  5
A2
330
9A
100
AcDbEntity
  8
0
100
AcDbVertex
100
AcDbPolyFaceMeshVertex
 10
0.0
 20
0.4434395109072581
 30
1.246368674020211
 70
   192
  0
VERTEX
  5
A3
330
9A
100
AcDbEntity
  8
0
 62
     1
100
AcDbFaceRecord
 10
0.0
 20
0.0
 30
0.0
 70
   128
 71
     1
 72
     2
 73
     3
 74
     4
  0
VERTEX
  5
A4
330
9A
100
AcDbEntity
  8
0
 62
     2
100
AcDbFaceRecord
 10
0.0
 20
0.0
 30
0.0
 70
   128
 71
     1
 72
     2
 73
     5
 74
     6
  0
VERTEX
  5
A5
330
9A
100
AcDbEntity
  8
0
 62
     3
100
AcDbFaceRecord
 10
0.0
 20
0.0
 30
0.0
 70
   128
 71
     2
 72
     3
 73
     7
 74
     5
  0
VERTEX
  5
A6
330
9A
100
AcDbEntity
  8
0
 62
     4
100
AcDbFaceRecord
 10
0.0
 20
0.0
 30
0.0
 70
   128
 71
     3
 72
     7
 73
     8
 74
     4
  0
VERTEX
  5
A7
330
9A
100
AcDbEntity
  8
0
 62
     5
100
AcDbFaceRecord
 10
0.0
 20
0.0
 30
0.0
 70
   128
 71
     1
 72
     4
 73
     8
 74
     6
  0
VERTEX
  5
A8
330
9A
100
AcDbEntity
  8
0
 62
     6
100
AcDbFaceRecord
 10
0.0
 20
0.0
 30
0.0
 70
   128
 71
     6
 72
     5
 73
     7
 74
     8
  0
SEQEND
  5
A9
330
9A
100
AcDbEntity
  8
0
  0
ENDSEC
"""
