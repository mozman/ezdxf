#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.acis.api import mesh_from_body, load
from ezdxf.acis.mesh import PolyhedronFaceBuilder
from ezdxf.render import forms


class TestPrismToMesh:
    """The "prism" is a distorted cube with quadrilateral faces at the
    top and bottom and eight triangles as connecting faces inbetween.
    """

    @pytest.fixture(scope="class")
    def mesh(self, prism_sat):
        body = load(prism_sat)[0]
        return mesh_from_body(body)[0]

    def test_mesh_has_10_faces(self, mesh):
        assert len(mesh.faces) == 10

    def test_mesh_has_8_unique_vertices(self, mesh):
        assert len(mesh.vertices) == 8

    def test_all_faces_have_at_least_3_vertices(self, mesh):
        assert all(len(set(face)) >= 3 for face in mesh.faces)

    def test_any_face_has_at_least_4_vertices(self, mesh):
        assert any(len(set(face)) == 4 for face in mesh.faces)


class TestPolyhedronFaceBuilder:
    @pytest.fixture
    def builder(self):
        return PolyhedronFaceBuilder(forms.cube())

    def test_six_faces_will_be_created(self, builder):
        """There have to be 6 cube faces."""
        faces = list(builder.acis_faces())
        assert len(faces) == 6

    def test_each_face_gets_it_own_plane(self, builder):
        """Each face has to have its own flat surface plane."""
        planes = {id(face.surface) for face in builder.acis_faces()}
        assert len(planes) == 6
        assert (
            all(
                face.surface.type == "plane-surface"
                for face in builder.acis_faces()
            )
            is True
        )

    def test_each_face_has_a_single_loop(self, builder):
        """The PolyhedronFaceBuilder supports only a single loop for each face,
        so divided faces or holes in faces are not supported.
        """
        for face in builder.acis_faces():
            assert face.loop.next_loop.is_none is True

    def test_for_24_unique_coedges(self, builder):
        """Each face has its own coedges which represent the face boundary and
        each coedge references a 'real' edge entity
        """
        coedges = set()
        for face in builder.acis_faces():
            for coedge in face.loop.coedges():
                coedges.add(id(coedge))
        assert len(coedges) == 24

    def test_for_12_unique_edges(self, builder):
        """There have to be 12 'real' cube edges."""
        edges = set()
        for face in builder.acis_faces():
            for coedge in face.loop.coedges():
                edges.add(id(coedge.edge))
        assert len(edges) == 12

    def test_each_edges_has_a_unique_straight_line(self, builder):
        """Each edge has to have a straight lines as base curve."""
        edges = []
        for face in builder.acis_faces():
            for coedge in face.loop.coedges():
                edges.append(coedge.edge)

        assert all(e.curve.type == "straight-curve" for e in edges) is True
        assert len({id(e.curve) for e in edges}) == 12

    def test_for_24_unique_vertices(self, builder):
        """Each edge has its own start- and end vertex which has a reference
        the 'real' point.
        """
        vertices = set()
        for face in builder.acis_faces():
            for coedge in face.loop.coedges():
                vertices.add(id(coedge.edge.start_vertex))
                vertices.add(id(coedge.edge.end_vertex))
        assert len(vertices) == 24

    def test_for_8_unique_points(self, builder):
        """There have to be 8 'real' cube corner points."""
        points = set()
        for face in builder.acis_faces():
            for coedge in face.loop.coedges():
                points.add(id(coedge.edge.start_vertex.point))
                points.add(id(coedge.edge.end_vertex.point))
        assert len(points) == 8


if __name__ == "__main__":
    pytest.main([__file__])
