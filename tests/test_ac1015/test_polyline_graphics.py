#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test basic graphic entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

import ezdxf
from ezdxf.const import VTX_3D_POLYLINE_VERTEX
from ezdxf.tools.test import DrawingProxy, Tags
from ezdxf.entitysection import EntitySection

DWG = ezdxf.new('AC1015')


class TestPolyline(unittest.TestCase):
    def setUp(self):
        self.layout = DWG.modelspace()

    def test_create_polyline2D(self):
        polyline = self.layout.add_polyline2d([(0, 0), (1, 1)])
        self.assertEqual((0., 0.), polyline[0].dxf.location)
        self.assertEqual((1., 1.), polyline[1].dxf.location)
        self.assertEqual('AcDb2dPolyline', polyline.get_mode())

    def test_create_polyline3D(self):
        polyline = self.layout.add_polyline3d([(1, 2, 3), (4, 5, 6)])
        self.assertEqual((1., 2., 3.), polyline[0].dxf.location)
        self.assertEqual((4., 5., 6.), polyline[1].dxf.location)
        self.assertEqual(VTX_3D_POLYLINE_VERTEX, polyline[0].dxf.flags)
        self.assertEqual('AcDb3dPolyline', polyline.get_mode())

    def test_set_vertex(self):
        polyline = self.layout.add_polyline2d([(0, 0), (1, 1), (2, 2), (3, 3)])
        polyline[2].dxf.location = (7, 7)
        self.assertEqual((7., 7.), polyline[2].dxf.location)

    def test_points(self):
        points = [(0, 0), (1, 1), (2, 2), (3, 3)]
        polyline = self.layout.add_polyline2d(points)
        self.assertEqual(points, list(polyline.points()))

    def test_point_slicing(self):
        points = [(0, 0), (1, 1), (2, 2), (3, 3)]
        polyline = self.layout.add_polyline2d(points)
        self.assertEqual([(1, 1), (2, 2)], list(polyline.points())[1:3])

    def test_append_vertices(self):
        polyline = self.layout.add_polyline2d([(0, 0), (1, 1)])
        polyline.append_vertices([(7, 7), (8, 8)])
        self.assertEqual((7., 7.), polyline[2].dxf.location)
        self.assertEqual(4, len(polyline))

    def test_insert_vertices(self):
        polyline = self.layout.add_polyline2d([(0, 0), (1, 1)])
        polyline.insert_vertices(0, [(7, 7), (8, 8)])
        self.assertEqual((7, 7), polyline[0].dxf.location)
        self.assertEqual((1, 1), polyline[3].dxf.location)
        self.assertEqual(4, len(polyline))

    def test_delete_one_vertex(self):
        polyline = self.layout.add_polyline2d([(0, 0), (1, 1), (2, 2), (3, 3)])
        polyline.delete_vertices(0)
        self.assertEqual((1, 1), polyline[0].dxf.location)
        self.assertEqual(3, len(polyline))

    def test_delete_two_vertices(self):
        polyline = self.layout.add_polyline2d([(0, 0), (1, 1), (2, 2), (3, 3)])
        polyline.delete_vertices(pos=0, count=2)
        self.assertEqual((2, 2), polyline[0].dxf.location)
        self.assertEqual(2, len(polyline))


class TestPolymesh(unittest.TestCase):
    def setUp(self):
        self.layout = DWG.modelspace()

    def test_create_mesh(self):
        mesh = self.layout.add_polymesh((4, 4))

    def test_set_vertex(self):
        mesh = self.layout.add_polymesh((4, 4))
        mesh.set_mesh_vertex((1, 1), (1, 2, 3))
        self.assertEqual((1, 2, 3), mesh.get_mesh_vertex((1, 1)).dxf.location)

    def test_error_n_index(self):
        mesh = self.layout.add_polymesh((4, 4))
        with self.assertRaises(IndexError):
            mesh.get_mesh_vertex((0, 4))

    def test_error_m_index(self):
        mesh = self.layout.add_polymesh((4, 4))
        with self.assertRaises(IndexError):
            mesh.get_mesh_vertex((4, 0))

    def test_mesh_cache(self):
        pos = (2, 1)
        mesh = self.layout.add_polymesh((4, 4))
        cache = mesh.get_mesh_vertex_cache()
        cache[pos] = (1, 2, 3)
        vertex = mesh.get_mesh_vertex(pos)
        self.assertEqual(vertex.dxf.location, cache[pos])
        with self.assertRaises(IndexError):
            cache[4, 0]


class TestPolyface(unittest.TestCase):
    def setUp(self):
        self.layout = DWG.modelspace()

    def test_create_face(self):
        face = self.layout.add_polyface()
        self.assertEqual(0, len(face))

    def test_add_face(self):
        face = self.layout.add_polyface()
        face.append_face([(0, 0), (1, 1), (2, 2), (3, 3)])
        self.assertEqual([(0, 0), (1, 1), (2, 2), (3, 3), (0, 0, 0)], list(face.points()))

    def test_face_indices(self):
        face = self.layout.add_polyface()
        face.append_face([(0, 0), (1, 1), (2, 2), (3, 3)])
        face_record = face[4]
        self.assertEqual(1, face_record.dxf.vtx0)
        self.assertEqual(2, face_record.dxf.vtx1)
        self.assertEqual(3, face_record.dxf.vtx2)
        self.assertEqual(4, face_record.dxf.vtx3)

    def test_add_two_face_indices(self):
        face = self.layout.add_polyface()
        face.append_face([(0, 0), (1, 1), (2, 2), (3, 3)])
        # second face has same vertices as the first face
        face.append_face([(0, 0), (1, 1), (2, 2)])
        face_record = face[5]  # second face
        self.assertEqual(1, face_record.dxf.vtx0)
        self.assertEqual(2, face_record.dxf.vtx1)
        self.assertEqual(3, face_record.dxf.vtx2)
        self.assertEqual(4, face.dxf.m_count)  # vertices count
        self.assertEqual(2, face.dxf.n_count)  # faces count

    def test_faces(self):
        face = self.layout.add_polyface()
        face.append_face([(0, 0), (1, 1), (2, 2), (3, 3)])
        face.append_face([(0, 0), (1, 1), (2, 2)])
        result = list(face.faces())
        self.assertEqual(2, len(result))
        points1 = [vertex.dxf.location for vertex in result[0]]
        # the last vertex is the face_record and is always (0,0,0)
        # the face_record contains indices to the face building vertices
        self.assertEqual([(0, 0), (1, 1), (2, 2), (3, 3), (0, 0, 0)], points1)

    def test_optimized_cube(self):
        face = self.layout.add_polyface()
        # a cube consist of 6 faces and 24 vertices
        # duplicated vertices should be removed
        face.append_faces(cube_faces())
        self.assertEqual(8, face.dxf.m_count)  # vertices count
        self.assertEqual(6, face.dxf.n_count)  # faces count


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


class TestInternals(unittest.TestCase):
    def setUp(self):
        self.layout = DWG.modelspace()

    def test_polyline2d(self):
        polyline = self.layout.add_polyline2d([(0, 0), (1, 1)])
        self.assertEqual('AcDb2dPolyline', polyline.tags.subclasses[2][0].value)
        vertex = polyline[0]
        self.assertEqual('AcDbVertex', vertex.tags.subclasses[2][0].value)
        self.assertEqual('AcDb2dVertex', vertex.tags.subclasses[3][0].value)

    def test_polyline3d(self):
        polyline = self.layout.add_polyline3d([(0, 0), (1, 1)])
        self.assertEqual('AcDb3dPolyline', polyline.tags.subclasses[2][0].value)
        vertex = polyline[0]
        self.assertEqual('AcDbVertex', vertex.tags.subclasses[2][0].value)
        self.assertEqual('AcDb3dPolylineVertex', vertex.tags.subclasses[3][0].value)

    def test_polymesh(self):
        mesh = self.layout.add_polymesh((4, 4))
        vertex = mesh[0]
        self.assertEqual('AcDbVertex', vertex.tags.subclasses[2][0].value)
        self.assertEqual('AcDbPolygonMeshVertex', vertex.tags.subclasses[3][0].value)

    def test_polyface(self):
        face = self.layout.add_polyface()
        face.append_face([(0, 0), (1, 1), (2, 2), (3, 3)])
        vertex = face[0]
        self.assertEqual('AcDbVertex', vertex.tags.subclasses[2][0].value)
        self.assertEqual('AcDbPolyFaceMeshVertex', vertex.tags.subclasses[3][0].value)

        vertex = face[4]
        self.assertFalse(len(vertex.tags.subclasses[2]))
        self.assertEqual('AcDbFaceRecord', vertex.tags.subclasses[3][0].value)


class TestNewStylePolyface(unittest.TestCase):

    def setUp(self):
        self.dwg = DrawingProxy('AC1018')
        self.section = EntitySection(Tags.from_text(NEW_STYLE_POLYFACE), self.dwg)

    def test_face_count(self):
        polyface = list(self.section)[0]
        faces = list(polyface.faces())
        self.assertEqual(6, len(faces))

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

if __name__ == '__main__':
    unittest.main()