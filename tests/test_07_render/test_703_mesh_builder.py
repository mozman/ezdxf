# Copyright (c) 2018-2022, Manfred Moitzi
# License: MIT License
import pytest
from math import radians
from ezdxf.math import Vec3, BoundingBox
from ezdxf.render.forms import cube, circle, cylinder, cone, sphere
from ezdxf.addons.menger_sponge import MengerSponge
from ezdxf.render.mesh import (
    MeshVertexMerger,
    MeshBuilder,
    MeshTransformer,
    MeshAverageVertexMerger,
    merge_connected_paths,
    merge_full_patch,
    NodeMergingError,
    DegeneratedPathError,
    remove_colinear_face_vertices,
    all_edges,
    get_edge_stats,
    separate_meshes,
)
from ezdxf.addons import SierpinskyPyramid
from ezdxf.layouts import VirtualLayout


def test_vertex_merger_indices():
    merger = MeshVertexMerger()
    indices = merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    indices2 = merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    assert indices == indices2


def test_vertex_merger_vertices():
    merger = MeshVertexMerger()
    merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    assert merger.vertices == [(1, 2, 3), (4, 5, 6)]


def test_vertex_merger_index_of():
    merger = MeshVertexMerger()
    merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    assert merger.index((1, 2, 3)) == 0
    assert merger.index((4, 5, 6)) == 1
    with pytest.raises(IndexError):
        merger.index((7, 8, 9))


def test_average_vertex_merger_indices():
    merger = MeshAverageVertexMerger()
    indices = merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    indices2 = merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    assert indices == indices2


def test_average_vertex_merger_vertices():
    merger = MeshAverageVertexMerger()
    merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    assert merger.vertices == [(1, 2, 3), (4, 5, 6)]


def test_average_vertex_merger_index_of():
    merger = MeshAverageVertexMerger()
    merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    assert merger.index((1, 2, 3)) == 0
    assert merger.index((4, 5, 6)) == 1
    with pytest.raises(IndexError):
        merger.index((7, 8, 9))


def test_mesh_builder(msp):
    pyramid = SierpinskyPyramid(level=4, sides=3)
    pyramid.render(msp, merge=False)
    meshes = msp.query("MESH")
    assert len(meshes) == 256


def test_vertex_merger():
    pyramid = SierpinskyPyramid(level=4, sides=3)
    faces = pyramid.faces()
    mesh = MeshVertexMerger()
    for vertices in pyramid:
        mesh.add_mesh(vertices=vertices, faces=faces)
    assert len(mesh.vertices) == 514
    assert len(mesh.faces) == 1024


def test_average_vertex_merger():
    pyramid = SierpinskyPyramid(level=4, sides=3)
    faces = pyramid.faces()
    mesh = MeshAverageVertexMerger()
    for vertices in pyramid:
        mesh.add_mesh(vertices=vertices, faces=faces)
    assert len(mesh.vertices) == 514
    assert len(mesh.faces) == 1024


REGULAR_FACE = Vec3.list([(0, 0, 0), (1, 0, 1), (1, 1, 1), (0, 1, 0)])
IRREGULAR_FACE = Vec3.list([(0, 0, 0), (1, 0, 1), (1, 1, 0), (0, 1, 0)])


def test_has_none_planar_faces():
    mesh = MeshBuilder()
    mesh.add_face(REGULAR_FACE)
    assert mesh.has_none_planar_faces() is False
    mesh.add_face(IRREGULAR_FACE)
    assert mesh.has_none_planar_faces() is True


def test_scale_mesh():
    mesh = cube(center=False)
    mesh.scale(2, 3, 4)
    bbox = BoundingBox(mesh.vertices)
    assert bbox.extmin.isclose((0, 0, 0))
    assert bbox.extmax.isclose((2, 3, 4))


def test_rotate_x():
    mesh = cube(center=False)
    mesh.rotate_x(radians(90))
    bbox = BoundingBox(mesh.vertices)
    assert bbox.extmin.isclose((0, -1, 0))
    assert bbox.extmax.isclose((1, 0, 1))


class TestMeshDiagnose:
    def test_empty_mesh_is_not_watertight(self):
        mesh = MeshBuilder()
        assert mesh.diagnose().euler_characteristic != 2

    def test_single_face_mesh_is_not_watertight(self):
        mesh = MeshBuilder()
        mesh.add_face(REGULAR_FACE)
        assert mesh.diagnose().euler_characteristic != 2

    def test_cube_is_watertight(self):
        mesh = cube(center=False)
        assert mesh.diagnose().euler_characteristic == 2

    def test_is_watertight_can_not_detect_vertex_orientation_errors(self):
        mesh = cube(center=False)
        mesh.faces[-1] = tuple(reversed(mesh.faces[-1]))
        assert (mesh.diagnose().euler_characteristic == 2)

    def test_edge_balance_of_closed_surface_is_not_broken(self):
        mesh = cube(center=False)
        assert mesh.diagnose().is_edge_balance_broken is False

    def test_edge_balance_of_wrong_oriented_faces_is_broken(self):
        mesh = cube(center=False)
        mesh.faces[-1] = tuple(reversed(mesh.faces[-1]))
        assert mesh.diagnose().is_edge_balance_broken is True

    def test_edge_balance_of_doubled_faces_is_broken(self):
        mesh = cube(center=False)
        mesh.faces.append(mesh.faces[-1])
        assert mesh.diagnose().is_edge_balance_broken is True

    def test_total_edge_count_of_closed_surface(self):
        mesh = cube(center=False)
        stats = mesh.diagnose()
        assert stats.total_edge_count() == stats.n_edges * 2

    def test_cube_of_separated_faces_is_not_watertight(self):
        mesh = cube(center=False)
        mesh2 = MeshBuilder()
        for face in mesh.faces_as_vertices():
            mesh2.add_face(face)
        assert mesh2.diagnose().euler_characteristic != 2

    def test_cylinder_is_watertight(self):
        mesh = cylinder()
        assert mesh.diagnose().euler_characteristic == 2

    @pytest.mark.parametrize("surface", [cube(), cylinder(), cone(), sphere()])
    def test_surface_normals_pointing_outwards(self, surface):
        diagnose = surface.diagnose()
        assert diagnose.estimate_normals_direction() > 0.9

    def test_cylinder_with_reversed_cap_normals(self):
        c = cylinder()
        for i, face in enumerate(c.faces):
            if len(face) > 4:
                c.faces[i] = tuple(reversed(c.faces[i]))
        diagnose = c.diagnose()
        assert diagnose.estimate_normals_direction() < 0.8
        assert diagnose.is_edge_balance_broken is True


def test_flipped_cube_normals_pointing_inwards():
    c = cube()
    c.flip_normals()
    diagnose = c.diagnose()
    assert diagnose.estimate_normals_direction() == pytest.approx(-1.0)


@pytest.fixture
def msp():
    return VirtualLayout()


@pytest.fixture(scope="module")
def cube_polyface():
    layout = VirtualLayout()
    p = layout.add_polyface()
    p.append_faces(cube().faces_as_vertices())
    return p


def test_from_empty_polyface(msp):
    empty_polyface = msp.add_polyface()
    b = MeshBuilder.from_polyface(empty_polyface)
    assert len(b.vertices) == 0
    assert len(b.faces) == 0


def test_from_cube_polyface(cube_polyface):
    b = MeshBuilder.from_polyface(cube_polyface)
    assert len(b.vertices) == 24  # unoptimized mesh builder
    assert len(b.faces) == 6


def test_render_polyface(cube_polyface, msp):
    t = MeshTransformer.from_polyface(cube_polyface)
    assert len(t.vertices) == 24  # unoptimized mesh builder
    assert len(t.faces) == 6
    t.render_polyface(msp)
    new_polyface = msp[-1]
    assert new_polyface.dxftype() == "POLYLINE"
    assert new_polyface.is_poly_face_mesh is True
    assert len(new_polyface.vertices) == 8 + 6
    assert new_polyface.vertices[0] is not cube_polyface.vertices[0]


def test_from_polymesh(msp):
    polymesh = msp.add_polymesh(size=(4, 4))
    b = MeshBuilder.from_polyface(polymesh)
    n = polymesh.dxf.n_count
    m = polymesh.dxf.m_count
    nfaces = (n - 1) * (m - 1)
    assert len(b.vertices) == nfaces * 4  # unoptimized mesh builder
    assert len(b.faces) == nfaces


def test_from_polyface_type_error(msp):
    polyline = msp.add_polyline3d([(0, 0, 0), (1, 0, 0)])
    with pytest.raises(TypeError):
        MeshBuilder.from_polyface(polyline)

    line = msp.add_line(start=(0, 0, 0), end=(1, 0, 0))
    with pytest.raises(TypeError):
        MeshBuilder.from_polyface(line)


@pytest.fixture
def polyface_181_1(msp):
    e = msp.new_entity(
        "POLYLINE",
        dxfattribs={
            "flags": 48,
            "m_count": 2,
            "n_count": 6,
        },
    )
    e.append_vertex(
        (25041.94191089287, 29272.95055566061, 0.0), dxfattribs={"flags": 64}
    )
    e.append_vertex(
        (25020.29127589287, 29285.45055566061, 0.0), dxfattribs={"flags": 64}
    )
    e.append_vertex(
        (25020.29127589287, 29310.45055566061, 0.0), dxfattribs={"flags": 64}
    )
    e.append_vertex(
        (25041.94191089287, 29322.95055566061, 0.0), dxfattribs={"flags": 64}
    )
    e.append_vertex(
        (25063.59254589287, 29310.45055566061, 0.0), dxfattribs={"flags": 64}
    )
    e.append_vertex(
        (25063.59254589287, 29285.45055566061, 0.0), dxfattribs={"flags": 64}
    )
    e.append_vertex(
        (25041.94191089287, 29272.95055566061, 50.0), dxfattribs={"flags": 64}
    )
    e.append_vertex(
        (25020.29127589287, 29285.45055566061, 50.0), dxfattribs={"flags": 64}
    )
    e.append_vertex(
        (25020.29127589287, 29310.45055566061, 50.0), dxfattribs={"flags": 64}
    )
    e.append_vertex(
        (25041.94191089287, 29322.95055566061, 50.0), dxfattribs={"flags": 64}
    )
    e.append_vertex(
        (25063.59254589287, 29310.45055566061, 50.0), dxfattribs={"flags": 64}
    )
    e.append_vertex(
        (25063.59254589287, 29285.45055566061, 50.0), dxfattribs={"flags": 64}
    )
    return e


def test_from_polyface_182_1(polyface_181_1):
    mesh = MeshVertexMerger.from_polyface(polyface_181_1)
    assert len(mesh.vertices) == 12


@pytest.fixture
def polyface_181_2(msp):
    e = msp.new_entity(
        "POLYLINE",
        dxfattribs={
            "flags": 16,
            "m_count": 6,
            "n_count": 3,
        },
    )
    e.append_vertex(
        (16606.65151901649, 81.88147523282441, 2099.9999999999995),
        dxfattribs={"flags": 64},
    )
    e.append_vertex(
        (16606.65151901649, 81.88147523282441, 1199.9999999999998),
        dxfattribs={"flags": 64},
    )
    e.append_vertex(
        (16606.65151901649, 81.88147523282441, 1199.9999999999998),
        dxfattribs={"flags": 64},
    )
    e.append_vertex(
        (16606.65151901649, 1281.8814752328244, 2099.9999999999995),
        dxfattribs={"flags": 64},
    )
    e.append_vertex(
        (16606.65151901649, 1281.8814752328244, 1199.9999999999998),
        dxfattribs={"flags": 64},
    )
    e.append_vertex(
        (16606.65151901649, 1281.8814752328244, 1199.9999999999998),
        dxfattribs={"flags": 64},
    )
    e.append_vertex(
        (16626.65151901649, 1281.8814752328244, 2099.9999999999995),
        dxfattribs={"flags": 64},
    )
    e.append_vertex(
        (16626.65151901649, 1281.8814752328244, 1199.9999999999998),
        dxfattribs={"flags": 64},
    )
    e.append_vertex(
        (16606.65151901649, 1281.8814752328244, 1199.9999999999998),
        dxfattribs={"flags": 64},
    )
    e.append_vertex(
        (16626.65151901649, 81.88147523282441, 2099.9999999999995),
        dxfattribs={"flags": 64},
    )
    e.append_vertex(
        (16626.65151901649, 81.88147523282441, 1199.9999999999998),
        dxfattribs={"flags": 64},
    )
    e.append_vertex(
        (16606.65151901649, 81.88147523282441, 1199.9999999999998),
        dxfattribs={"flags": 64},
    )
    e.append_vertex(
        (16626.65151901649, 81.88147523282441, 2099.9999999999995),
        dxfattribs={"flags": 64},
    )
    e.append_vertex(
        (16626.65151901649, 81.88147523282441, 2099.9999999999995),
        dxfattribs={"flags": 64},
    )
    e.append_vertex(
        (16606.65151901649, 81.88147523282441, 2099.9999999999995),
        dxfattribs={"flags": 64},
    )
    e.append_vertex(
        (16626.65151901649, 1281.8814752328244, 2099.9999999999995),
        dxfattribs={"flags": 64},
    )
    e.append_vertex(
        (16626.65151901649, 1281.8814752328244, 2099.9999999999995),
        dxfattribs={"flags": 64},
    )
    e.append_vertex(
        (16606.65151901649, 1281.8814752328244, 2099.9999999999995),
        dxfattribs={"flags": 64},
    )
    return e


def test_from_polyface_182_2(polyface_181_2):
    mesh = MeshVertexMerger.from_polyface(polyface_181_2)
    assert len(mesh.vertices) == 8


def test_mesh_subdivide():
    c = cube().scale_uniform(10).subdivide(2)
    assert len(c.vertices) == 2 * 25 + 3 * 16
    assert len(c.faces) == 16 * 6


def test_debug_coplanar_faces():
    source = MeshBuilder()
    source.vertices = [
        Vec3(-5.0, -5.0, -5.0),  # 0
        Vec3(-5.0, 0.0, -5.0),  # 1
        Vec3(0.0, 0.0, -5.0),  # 2
        Vec3(0.0, -5.0, -5.0),  # 3
        Vec3(-5.0, 5.0, -5.0),  # 4
        Vec3(0.0, 5.0, -5.0),  # 5
        Vec3(5.0, 5.0, -5.0),  # 6
        Vec3(5.0, 0.0, -5.0),  # 7
        Vec3(5.0, -5.0, -5.0),  # 8
    ]
    source.faces = [
        (0, 1, 2, 3),
        (4, 5, 2, 1),
        (6, 7, 2, 5),
        (8, 3, 2, 7),
    ]
    optimized_cube = source.merge_coplanar_faces()
    assert len(optimized_cube.faces) == 1
    assert len(optimized_cube.vertices) == 4


def test_merge_coplanar_faces():
    c = cube().scale_uniform(10).subdivide(1)
    assert len(c.vertices) == 26
    assert len(c.faces) == 24
    optimized_cube = c.merge_coplanar_faces()
    assert len(optimized_cube.faces) == 6
    assert len(optimized_cube.vertices) == 8


def test_merge_disk():
    m = MeshVertexMerger()
    vertices = list(circle(8, close=True))
    for v1, v2 in zip(vertices, vertices[1:]):
        m.add_face([Vec3(), v1, v2])
    assert len(m.vertices) == 9
    assert len(m.faces) == 8

    m2 = m.merge_coplanar_faces()
    assert len(m2.vertices) == 8
    assert len(m2.faces) == 1


def test_merge_coplanar_faces_in_two_passes():
    c = cube().scale_uniform(10).subdivide(2)
    assert len(c.vertices) == 98
    assert len(c.faces) == 96
    optimized_cube = c.merge_coplanar_faces(passes=2)
    assert len(optimized_cube.faces) == 6
    assert len(optimized_cube.vertices) == 8


class TestMergeConnectedPaths:
    @pytest.mark.parametrize(
        "p",
        [
            [1, 2, 3],
            [3, 2, 1],
            [1, 2, 3, 4, 5],
        ],
    )
    def test_non_connected_paths(self, p):
        assert merge_connected_paths(p, [17, 18, 19]) == p

    def test_connected_squares_same_orientation(self):
        # fmt: off
        assert merge_connected_paths([1, 2, 3, 4], [4, 3, 5, 6]) == [
            1, 2, 3, 5, 6, 4,
        ]
        assert merge_connected_paths([1, 2, 3, 4], [4, 5, 6, 1]) == [
            1, 2, 3, 4, 5, 6
        ]
        # fmt: on

    def test_connected_squares_different_orientation(self):
        """The connected structure have to have the same orientation (clockwise
        or counter-clockwise to be merged.
        """
        # fmt: off
        assert merge_connected_paths([1, 2, 3, 4], [6, 5, 3, 4]) == [
            1, 2, 3, 4
        ]
        # fmt: on

    def test_connected_rect_same_orientation(self):
        # fmt: off
        assert merge_connected_paths([1, 2, 3, 4, 5, 6], [6, 5, 4, 7, 8, 9]) == [
            1, 2, 3, 4, 7, 8, 9, 6
        ]
        # fmt: on

    def test_complex_shape(self):
        # fmt: off
        assert merge_connected_paths(
            [1, 2, 3, 4, 5, 6, 7, 8],
            [6, 9, 10, 11, 8, 7],
        ) == [
            1, 2, 3, 4, 5, 6, 9, 10, 11, 8,
        ]
        # fmt: on

    def test_connected_by_one_vertex(self):
        with pytest.raises(NodeMergingError):
            merge_connected_paths([1, 2, 3, 4], [5, 6, 7, 4])

    @pytest.mark.parametrize(
        "p2",
        [
            [5, 6, 7, 4],
            [5, 6, 7, 4, 8],
            [5, 6, 7, 4, 8, 9],
        ],
    )
    def test_connection_error(self, p2):
        with pytest.raises(NodeMergingError):
            merge_connected_paths([1, 2, 3, 4], p2)

    def test_merge_multiple_paths(self):
        p1 = [1, 2, 9, 8]
        p2 = [3, 4, 9, 2]
        p3 = [5, 6, 9, 4]
        p4 = [7, 8, 9, 6]
        p = merge_connected_paths(p1, p2)
        assert p == [1, 2, 3, 4, 9, 8]
        p = merge_connected_paths(p, p3)
        assert p == [1, 2, 3, 4, 5, 6, 9, 8]
        p = merge_connected_paths(p, p4)
        assert p == [1, 2, 3, 4, 5, 6, 7, 8]

    def test_degenerated_path(self):
        """This creates a path [0, 1] which is invalid."""
        open_segments = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        closing_segment = [0, 8, 1]
        with pytest.raises(DegeneratedPathError):
            merge_connected_paths(open_segments, closing_segment)


class TestRemoveColinearVertices:
    @pytest.mark.parametrize(
        "v",
        [
            [],
            [Vec3(0, 0)],
            [Vec3(0, 0), Vec3(1, 0)],
        ],
    )
    def test_simple_cases_without_action(self, v):
        assert list(remove_colinear_face_vertices(v)) == v

    @pytest.mark.parametrize(
        "v",
        [
            [Vec3(0, 0), Vec3(1, 0), Vec3(2, 0)],
            [Vec3(0, 0), Vec3(1, 0), Vec3(2, 0), Vec3(3, 0)],
        ],
    )
    def test_remove_in_between_vertices(self, v):
        assert list(remove_colinear_face_vertices(v)) == [v[0], v[-1]]

    @pytest.mark.parametrize(
        "v",
        [
            [Vec3(0, 0), Vec3(0, 0), Vec3(2, 0)],
            [Vec3(0, 0), Vec3(0, 0), Vec3(0, 0), Vec3(3, 0)],
            [Vec3(0, 0), Vec3(0, 0), Vec3(0, 0), Vec3(0, 0)],
            [Vec3(1, 0), Vec3(1, 0), Vec3(0, 2), Vec3(0, 2)],
        ],
    )
    def test_remove_duplicated_vertices(self, v):
        assert list(remove_colinear_face_vertices(v)) == [v[0], v[-1]]

    def test_remove_in_between_vertices_with_direction_change(self):
        v = [
            Vec3(0, 0),
            Vec3(1, 0),
            Vec3(2, 0),
            Vec3(2, 1),
            Vec3(2, 2),
            Vec3(2, 3),
        ]
        assert list(remove_colinear_face_vertices(v)) == [v[0], v[2], v[-1]]

    def test_subdivided_square(self):
        v = [
            Vec3(-5.0, -5.0, -5.0),
            Vec3(-5.0, 0.0, -5.0),
            Vec3(-5.0, 5.0, -5.0),
            Vec3(0.0, 5.0, -5.0),
            Vec3(5.0, 5.0, -5.0),
            Vec3(5.0, 0.0, -5.0),
            Vec3(5.0, -5.0, -5.0),
            Vec3(0.0, -5.0, -5.0),
        ]
        assert list(remove_colinear_face_vertices(v)) == [
            v[0],
            v[2],
            v[4],
            v[6],
        ]


class TestMergeFullPatch:
    @pytest.mark.parametrize(
        "seg",
        [
            [0, 8, 1],
            [1, 0, 8],
            [8, 1, 0],
        ],
    )
    def test_fill_pie(self, seg):
        open_pie = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        res = merge_full_patch(open_pie, seg)
        assert res == [1, 2, 3, 4, 5, 6, 7, 8]


def test_all_edges_cube():
    mesh = cube()
    edges = list(all_edges(mesh.faces))
    assert len(edges) == 6 * 4
    assert len(set(edges)) == 24


class TestGetEdgeStats:
    @pytest.fixture(scope="class")
    def edges(self):
        mesh = cube()
        return get_edge_stats(mesh.faces)

    def test_unique_edge_count(self, edges):
        assert len(edges) == 12

    def test_sum_of_edge_count(self, edges):
        assert sum(e[0] for e in edges.values()) == 24

    def test_all_balances_are_0(self, edges):
        assert all(e[1] == 0 for e in edges.values()) is True

    def test_invalid_face_orientation_break_the_rules(self):
        faces = cube().faces
        faces[-1] = list(reversed(faces[-1]))
        edges = get_edge_stats(faces)
        assert all(e[1] == 0 for e in edges.values()) is False

    def test_coincident_faces_break_the_rules(self):
        faces = cube().faces
        faces.append(faces[-1])
        edges = get_edge_stats(faces)
        assert all(e[1] == 0 for e in edges.values()) is False

    def test_edge_balance_has_no_meaning_for_open_surfaces(self):
        faces = [(0, 1, 2)]
        edges = get_edge_stats(faces)
        assert all(e[1] != 0 for e in edges.values()) is True


def test_euler_characteristic_for_menger_sponge():
    """The euler characteristic does not work for non-convex meshes."""
    ms = MengerSponge()
    diag = ms.mesh().diagnose()
    assert diag.euler_characteristic == 40
    # the is_watertight property not reliable for concave meshes
    # each edge connects two faces
    assert diag.is_edge_balance_broken is False


class TestSeparateMeshes:
    def test_separate_a_single_cube_returns_a_single_cube(self):
        c1 = cube()
        result = list(separate_meshes(c1))
        assert len(result) == 1
        c2 = result[0]
        # vertex and face structure keeps stable for single meshes:
        assert c1.vertices == c2.vertices
        assert c1.faces == c2.faces

    def test_separate_menger_sponge(self):
        m1 = MengerSponge().mesh()
        result = list(separate_meshes(m1))
        assert len(result) == 1
        m2 = result[0]
        # vertex and face structure keeps stable for single meshes:
        assert m1.vertices == m2.vertices
        assert m1.faces == m2.faces

    def test_separate_two_cubes(self):
        cubes = cube()
        cubes.translate(10, 0, 0)
        cubes.add_mesh(mesh=cube())
        # a non-broken edge balance is a requirement to work properly:
        assert cubes.diagnose().is_edge_balance_broken is False
        result = list(separate_meshes(cubes))
        assert len(result) == 2

    def test_separate_two_intersecting_cubes(self):
        cubes = cube()
        cubes.translate(0.2, 0.2, 0.2)
        cubes.add_mesh(mesh=cube())
        # a non-broken edge balance is a requirement to work properly:
        assert cubes.diagnose().is_edge_balance_broken is False
        assert len(cubes.separate_meshes()) == 2

