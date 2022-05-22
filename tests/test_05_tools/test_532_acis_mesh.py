#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.acis.api import mesh_from_body, load, body_from_mesh
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
        assert len(builder.acis_faces()) == 6

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
        coedges = get_coedges(builder.acis_faces())
        assert len(coedges) == 24

    def test_for_partner_coedges(self, builder):
        """Each coedge has to have a partner coedge in the adjacent face and
        because they are sharing the same 'real' edge they have to have an
        opposite sense.
        """
        for coedge in get_coedges(builder.acis_faces()):
            partner_coedge = coedge.partner_coedge
            assert partner_coedge.is_none is False
            assert coedge.sense is not partner_coedge.sense
            assert partner_coedge.partner_coedge is coedge, "is back linked"

    def test_for_12_unique_edges(self, builder):
        """There have to be 12 'real' cube edges."""
        edges = get_edges(builder.acis_faces())
        assert len(edges) == 12

    def test_each_edges_has_a_unique_straight_line(self, builder):
        """Each edge has to have a straight lines as base curve."""
        edges = get_edges(builder.acis_faces())
        assert all(e.curve.type == "straight-curve" for e in edges) is True
        assert len(edges) == 12

    def test_for_24_unique_vertices(self, builder):
        """Each edge has its own start- and end vertex which has a reference
        the 'real' point.
        """
        vertices = get_vertices(builder.acis_faces())
        assert len(vertices) == 24

    def test_for_8_unique_points(self, builder):
        """There have to be 8 'real' cube corner points."""
        points = get_points(builder.acis_faces())
        assert len(points) == 8

    def test_build_multiple_times_independent_faces(self, builder):
        """The two builds should not share any data."""
        faces1 = builder.acis_faces()
        faces2 = builder.acis_faces()
        assert set(faces1).isdisjoint(set(faces2))
        assert set(get_coedges(faces1)).isdisjoint(set(get_coedges(faces2)))
        assert set(get_edges(faces1)).isdisjoint(set(get_edges(faces2)))
        assert set(get_vertices(faces1)).isdisjoint(set(get_vertices(faces2)))
        assert set(get_points(faces1)).isdisjoint(set(get_points(faces2)))


def get_coedges(faces):
    coedges = set()
    for face in faces:
        for coedge in face.loop.coedges():
            coedges.add(coedge)
    return coedges


def get_edges(faces):
    edges = set()
    for face in faces:
        for coedge in face.loop.coedges():
            edges.add(coedge.edge)
    return edges


def get_vertices(faces):
    vertices = set()
    for face in faces:
        for coedge in face.loop.coedges():
            vertices.add(coedge.edge.start_vertex)
            vertices.add(coedge.edge.end_vertex)
    return vertices


def get_points(faces):
    points = set()
    for face in faces:
        for coedge in face.loop.coedges():
            points.add(coedge.edge.start_vertex.point)
            points.add(coedge.edge.end_vertex.point)
    return points


def test_rebuild_mesh_from_acis_body():
    """Convert a cube-mesh into an ACIS body and the ACIS body back to a
    MeshBuilder instance.
    """
    cube = forms.cube()
    body = body_from_mesh(cube)
    cube2 = mesh_from_body(body)[0]
    assert set(cube.vertices) == set(cube2.vertices)
    assert faces_set(cube) == faces_set(cube2)


def faces_set(mesh):
    return set([tuple(face) for face in mesh.faces_as_vertices()])


if __name__ == "__main__":
    pytest.main([__file__])
