#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test basic graphic entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from tests.tools import DrawingProxy
from ezdxf.entityspace import EntitySpace

from ezdxf.ac1009.layouts import AC1009Layout
from ezdxf.const import VTX_3D_POLYLINE_VERTEX

class TestPolyline(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingProxy('AC1009')
        self.entityspace = EntitySpace(self.dwg.entitydb)
        self.layout = AC1009Layout(self.entityspace, self.dwg.dxffactory, 0)

    def test_create_polyline2D(self):
        polyline = self.layout.add_polyline2D( [(0, 0), (1, 1)] )
        self.assertEqual((0., 0.), polyline[0].location)
        self.assertEqual((1., 1.), polyline[1].location)
        self.assertEqual('polyline2d', polyline.getmode())

    def test_create_polyline3D(self):
        polyline = self.layout.add_polyline3D( [(1, 2, 3), (4, 5, 6)] )
        self.assertEqual((1., 2., 3.), polyline[0].location)
        self.assertEqual((4., 5., 6.), polyline[1].location)
        self.assertEqual(VTX_3D_POLYLINE_VERTEX, polyline[0].flags)
        self.assertEqual('polyline3d', polyline.getmode())

    def test_set_vertex(self):
        polyline = self.layout.add_polyline2D( [(0, 0), (1, 1), (2, 2), (3, 3)] )
        polyline[2].location = (7, 7)
        self.assertEqual((7., 7.), polyline[2].location)

    def test_points(self):
        points = [(0, 0), (1, 1), (2, 2), (3, 3)]
        polyline = self.layout.add_polyline2D(points)
        self.assertEqual(points, polyline.points)

    def test_point_slicing(self):
        points = [(0, 0), (1, 1), (2, 2), (3, 3)]
        polyline = self.layout.add_polyline2D(points)
        self.assertEqual([(1, 1), (2, 2)], polyline.points[1:3])

    def test_append_vertices(self):
        polyline = self.layout.add_polyline2D( [(0, 0), (1, 1)] )
        polyline.append_vertices([(7, 7), (8, 8)])
        self.assertEqual((7., 7.), polyline[2].location)
        self.assertEqual(4, len(polyline))

    def test_insert_vertices(self):
        polyline = self.layout.add_polyline2D( [(0, 0), (1, 1)] )
        polyline.insert_vertices(0, [(7, 7), (8, 8)])
        self.assertEqual((7, 7), polyline[0].location)
        self.assertEqual((1, 1), polyline[3].location)
        self.assertEqual(4, len(polyline))

    def test_delete_one_vertex(self):
        polyline = self.layout.add_polyline2D( [(0, 0), (1, 1), (2, 2), (3, 3)] )
        polyline.delete_vertices(0)
        self.assertEqual((1, 1), polyline[0].location)
        self.assertEqual(3, len(polyline))

    def test_delete_two_vertices(self):
        polyline = self.layout.add_polyline2D( [(0, 0), (1, 1), (2, 2), (3, 3)] )
        polyline.delete_vertices(pos=0, count=2)
        self.assertEqual((2, 2), polyline[0].location)
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
        self.assertEqual((1,2,3), mesh.get_mesh_vertex( (1, 1) ).location)

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
        self.assertEqual(1, facevertex.vtx0)
        self.assertEqual(2, facevertex.vtx1)
        self.assertEqual(3, facevertex.vtx2)
        self.assertEqual(4, facevertex.vtx3)

    def test_add_two_face_indices(self):
        face = self.layout.add_polyface()
        face.append_face([(0,0), (1,1), (2,2), (3,3)])
        face.append_face([(0,0), (1,1), (2,2)])
        facevertex = face[8]
        self.assertEqual(6, facevertex.vtx0)
        self.assertEqual(7, facevertex.vtx1)
        self.assertEqual(8, facevertex.vtx2)
        self.assertEqual(9, len(face))

    def test_faces(self):
        face = self.layout.add_polyface()
        face.append_face([(0,0), (1,1), (2,2), (3,3)])
        face.append_face([(0,0), (1,1), (2,2)])
        result = list(face.faces())
        self.assertEqual(2, len(result))
        points1 = [vertex.location for vertex in result[0]]
        self.assertEqual( [(0,0), (1,1), (2,2), (3,3)], points1 )

if __name__=='__main__':
    unittest.main()