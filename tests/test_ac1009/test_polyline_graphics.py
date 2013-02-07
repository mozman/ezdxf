#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test basic graphic entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

from ezdxf.testtools import DrawingProxy
from ezdxf.entityspace import EntitySpace

from ezdxf.ac1009.layouts import AC1009Layout
from ezdxf.const import VTX_3D_POLYLINE_VERTEX

class TestPolyline(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingProxy('AC1009')
        self.entityspace = EntitySpace(self.dwg.entitydb)
        self.layout = AC1009Layout(self.entityspace, self.dwg.dxffactory, 0)

    def test_create_polyline2D(self):
        polyline = self.layout.add_polyline2d( [(0, 0), (1, 1)] )
        self.assertEqual((0., 0.), polyline[0].dxf.location)
        self.assertEqual((1., 1.), polyline[1].dxf.location)
        self.assertEqual('polyline2d', polyline.getmode())

    def test_create_polyline3D(self):
        polyline = self.layout.add_polyline3d( [(1, 2, 3), (4, 5, 6)] )
        self.assertEqual((1., 2., 3.), polyline[0].dxf.location)
        self.assertEqual((4., 5., 6.), polyline[1].dxf.location)
        self.assertEqual(VTX_3D_POLYLINE_VERTEX, polyline[0].dxf.flags)
        self.assertEqual('polyline3d', polyline.getmode())

    def test_set_vertex(self):
        polyline = self.layout.add_polyline2d( [(0, 0), (1, 1), (2, 2), (3, 3)] )
        polyline[2].dxf.location = (7, 7)
        self.assertEqual((7., 7.), polyline[2].dxf.location)

    def test_points(self):
        points = [(0, 0), (1, 1), (2, 2), (3, 3)]
        polyline = self.layout.add_polyline2d(points)
        self.assertEqual(points, polyline.points)

    def test_point_slicing(self):
        points = [(0, 0), (1, 1), (2, 2), (3, 3)]
        polyline = self.layout.add_polyline2d(points)
        self.assertEqual([(1, 1), (2, 2)], polyline.points[1:3])

    def test_append_vertices(self):
        polyline = self.layout.add_polyline2d( [(0, 0), (1, 1)] )
        polyline.append_vertices([(7, 7), (8, 8)])
        self.assertEqual((7., 7.), polyline[2].dxf.location)
        self.assertEqual(4, len(polyline))

    def test_insert_vertices(self):
        polyline = self.layout.add_polyline2d( [(0, 0), (1, 1)] )
        polyline.insert_vertices(0, [(7, 7), (8, 8)])
        self.assertEqual((7, 7), polyline[0].dxf.location)
        self.assertEqual((1, 1), polyline[3].dxf.location)
        self.assertEqual(4, len(polyline))

    def test_delete_one_vertex(self):
        polyline = self.layout.add_polyline2d( [(0, 0), (1, 1), (2, 2), (3, 3)] )
        polyline.delete_vertices(0)
        self.assertEqual((1, 1), polyline[0].dxf.location)
        self.assertEqual(3, len(polyline))

    def test_delete_two_vertices(self):
        polyline = self.layout.add_polyline2d( [(0, 0), (1, 1), (2, 2), (3, 3)] )
        polyline.delete_vertices(pos=0, count=2)
        self.assertEqual((2, 2), polyline[0].dxf.location)
        self.assertEqual(2, len(polyline))

class TestPolymesh(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingProxy('AC1009')
        self.entityspace = EntitySpace(self.dwg.entitydb)
        self.layout = AC1009Layout(self.entityspace, self.dwg.dxffactory, 0)

    def test_create_mesh(self):
        mesh = self.layout.add_polymesh( (4, 4) )

    def test_set_vertex(self):
        mesh = self.layout.add_polymesh( (4, 4) )
        mesh.set_mesh_vertex( (1, 1), (1,2,3))
        self.assertEqual((1,2,3), mesh.get_mesh_vertex( (1, 1) ).dxf.location)

    def test_error_nindex(self):
        mesh = self.layout.add_polymesh( (4, 4) )
        with self.assertRaises(IndexError):
            mesh.get_mesh_vertex( (0, 4) )

    def test_error_mindex(self):
        mesh = self.layout.add_polymesh( (4, 4) )
        with self.assertRaises(IndexError):
            mesh.get_mesh_vertex( (4, 0) )

class TestPolyface(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingProxy('AC1009')
        self.entityspace = EntitySpace(self.dwg.entitydb)
        self.layout = AC1009Layout(self.entityspace, self.dwg.dxffactory, 0)

    def test_create_face(self):
        face = self.layout.add_polyface()
        self.assertEqual(0, len(face))

    def test_add_face(self):
        face = self.layout.add_polyface()
        face.append_face([(0,0), (1,1), (2,2), (3,3)])
        self.assertEqual([(0,0), (1,1), (2,2), (3,3), (0,0,0)], face.points)

    def test_face_indices(self):
        face = self.layout.add_polyface()
        face.append_face([(0,0), (1,1), (2,2), (3,3)])
        facevertex = face[4]
        self.assertEqual(1, facevertex.dxf.vtx0)
        self.assertEqual(2, facevertex.dxf.vtx1)
        self.assertEqual(3, facevertex.dxf.vtx2)
        self.assertEqual(4, facevertex.dxf.vtx3)

    def test_add_two_face_indices(self):
        face = self.layout.add_polyface()
        face.append_face([(0,0), (1,1), (2,2), (3,3)])
        # second face has same vertices as the first face
        face.append_face([(0,0), (1,1), (2,2)])
        facevertex = face[5] # second face
        self.assertEqual(1, facevertex.dxf.vtx0)
        self.assertEqual(2, facevertex.dxf.vtx1)
        self.assertEqual(3, facevertex.dxf.vtx2)
        self.assertEqual(4, face.dxf.mcount) # vertices count
        self.assertEqual(2, face.dxf.ncount) # faces count

    def test_faces(self):
        face = self.layout.add_polyface()
        face.append_face([(0,0), (1,1), (2,2), (3,3)])
        face.append_face([(0,0), (1,1), (2,2)])
        result = list(face.faces())
        self.assertEqual(2, len(result))
        points1 = [vertex.dxf.location for vertex in result[0]]
        # the last vertex is the face-vertex and is always (0,0,0)
        # the face-vertex contains indices to the face building vertices
        self.assertEqual( [(0,0), (1,1), (2,2), (3,3), (0,0,0)], points1 )

    def test_optimized_cube(self):
        face = self.layout.add_polyface()
        # a cube consist of 6 faces and 24 vertices
        # duplicated vertices should be removed
        face.append_faces(cube_faces())
        self.assertEqual(8, face.dxf.mcount) # vertices count
        self.assertEqual(6, face.dxf.ncount) # faces count

def cube_faces():
    # cube corner points
    p1 = (0,0,0)
    p2 = (0,0,1)
    p3 = (0,1,0)
    p4 = (0,1,1)
    p5 = (1,0,0)
    p6 = (1,0,1)
    p7 = (1,1,0)
    p8 = (1,1,1)

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

if __name__=='__main__':
    unittest.main()