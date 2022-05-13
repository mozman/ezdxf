#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf import acis


class TestPrismToMesh:
    """The "prism" is a distorted cube with quadrilateral faces at the
    top and bottom and eight triangles as connecting faces inbetween.
    """
    @pytest.fixture(scope="class")
    def mesh(self, prism_sat):
        body = acis.load(prism_sat)[0]
        return acis.mesh.from_body(body)[0]

    def test_mesh_has_10_faces(self, mesh):
        assert len(mesh.faces) == 10

    def test_mesh_has_8_unique_vertices(self, mesh):
        assert len(mesh.vertices) == 8

    def test_all_faces_have_at_least_3_vertices(self, mesh):
        assert all(len(set(face)) >= 3 for face in mesh.faces)

    def test_any_face_has_at_least_4_vertices(self, mesh):
        assert any(len(set(face)) == 4 for face in mesh.faces)


if __name__ == "__main__":
    pytest.main([__file__])
