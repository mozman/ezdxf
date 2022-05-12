#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf import acis


def test_flat_polygon_faces_from_body(prism_sat):
    bodies = acis.load(prism_sat)
    lumps = list(acis.mesh.flat_polygon_faces_from_body(bodies[0]))
    assert len(lumps) == 1
    faces = lumps[0]
    assert len(faces) == 10


def test_get_all_points(prism_sat):
    bodies = acis.load(prism_sat)
    face = bodies[0].lump.shell.face
    vertices = set()
    while not face.is_none:
        first_coedge = face.loop.coedge
        coedge = first_coedge
        while True:
            vertices.add(coedge.edge.start_vertex.point.location.round(4))
            coedge = coedge.next_coedge
            if coedge is first_coedge:
                break
        face = face.next_face
    assert len(vertices) == 8


def broken_test_mesh_from_body(prism_sat):
    bodies = acis.load(prism_sat)
    meshes = acis.mesh.from_body(bodies[0])
    assert len(meshes) == 1
    mesh = meshes[0]
    assert len(mesh.faces) == 10
    assert len(mesh.vertices) == 8


if __name__ == '__main__':
    pytest.main([__file__])
