#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf import acis


@pytest.fixture(scope="module")
def body(prism_sat):
    return acis.load(prism_sat)[0]


def test_all_polygon_faces_have_at_least_3_vertices(body):
    lumps = list(acis.mesh.flat_polygon_faces_from_body(body))
    assert all(len(set(face)) >= 3 for face in lumps[0])


def test_mesh_from_body(body):
    meshes = acis.mesh.from_body(body)
    assert len(meshes) == 1
    mesh = meshes[0]
    assert len(mesh.faces) == 10
    assert len(mesh.vertices) == 8


if __name__ == "__main__":
    pytest.main([__file__])
