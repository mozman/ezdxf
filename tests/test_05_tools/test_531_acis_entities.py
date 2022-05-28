#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.acis.api import load, export_sat, export_sab, ExportError
from ezdxf.acis import sat, sab, entities, hdr, const, mesh
from ezdxf.math import Matrix44
import math


def test_load_any_format(any_cube):
    bodies = load(any_cube)
    assert len(bodies) == 1


@pytest.fixture(scope="module")
def body(any_cube):
    return load(any_cube)[0]


class TestBody:
    def test_type_type(self, body):
        assert body.type == "body"

    def test_has_transform_attribute(self, body):
        assert body.transform.is_none is False

    def test_transform_attribute_was_loaded(self, body):
        m = body.transform.matrix
        assert m.get_row(3) == (388.5, 388.5, 388.5, 1.0)

    def test_has_wire_attribute(self, body):
        assert body.wire.is_none is True

    def test_get_all_lumps_as_a_list(self, body):
        bodies = body.lumps()
        assert len(bodies) == 1
        assert isinstance(bodies[0], entities.Lump)

    def test_append_lumps(self):
        body = entities.Body()
        assert len(body.lumps()) == 0
        body.append_lump(entities.Lump())
        assert len(body.lumps()) == 1
        body.append_lump(entities.Lump())
        assert len(body.lumps()) == 2


class TestLump:
    def test_lump_type(self, body):
        assert body.lump.type == "lump"

    def test_back_pointer_to_body(self, body):
        assert body.lump.body is body

    def test_has_no_next_lump(self, body):
        assert body.lump.next_lump.is_none is True

    def test_has_attribute_to_first_shell(self, body):
        assert body.lump.shell.is_none is False

    def test_get_all_shells_as_a_list(self, body):
        shells = body.lump.shells()
        assert len(shells) == 1
        assert isinstance(shells[0], entities.Shell)

    def test_append_shells(self):
        body = entities.Body()
        lump = entities.Lump()
        body.append_lump(lump)
        assert len(lump.shells()) == 0
        lump.append_shell(entities.Shell())
        assert len(lump.shells()) == 1
        lump.append_shell(entities.Shell())
        assert len(lump.shells()) == 2


class TestShell:
    @pytest.fixture(scope="class")
    def shell(self, body):
        return body.lump.shell

    def test_shell_type(self, shell):
        assert shell.type == "shell"

    def test_back_pointer_to_lump(self, shell):
        assert shell.lump.shell is shell

    def test_has_no_next_shell(self, shell):
        assert shell.next_shell.is_none is True

    def test_get_all_faces_as_a_list(self, shell):
        faces = shell.faces()
        assert len(faces) == 6
        assert isinstance(faces[0], entities.Face)

    def test_append_faces(self):
        body = entities.Body()
        lump = entities.Lump()
        shell = entities.Shell()
        body.append_lump(lump)
        lump.append_shell(shell)

        assert len(shell.faces()) == 0
        shell.append_face(entities.Face())
        assert len(shell.faces()) == 1
        shell.append_face(entities.Face())
        assert len(shell.faces()) == 2


class TestFace:
    @pytest.fixture(scope="class")
    def face(self, body):
        return body.lump.shell.face

    def test_face_type(self, face):
        assert face.type == "face"

    def test_back_pointer_to_shell(self, body, face):
        assert face.shell is body.lump.shell

    def test_has_attribute_surface(self, face):
        assert face.surface.type == "plane-surface"

    def test_face_features(self, face):
        assert face.sense is False  # forward
        assert face.double_sided is False  # single
        assert face.containment is False

    def test_traverse_all_six_cube_faces(self, face):
        count = 1
        while not face.next_face.is_none:
            count += 1
            face = face.next_face
        assert count == 6


class TestPolyhedronFaceBuilder:
    @pytest.fixture(scope="class")
    def cube(self):
        from ezdxf.render.forms import cube
        return mesh.PolyhedronFaceBuilder(cube())

    def test_creates_six_faces(self, cube):
        faces = list(cube.acis_faces())
        assert len(faces) == 6

    def test_each_face_defines_a_plane_surface(self, cube):
        for face in cube.acis_faces():
            assert face.surface.type == "plane-surface"


class TestPlane:
    @pytest.fixture(scope="class")
    def plane(self, body):
        return body.lump.shell.face.surface

    def test_plane_type(self, plane):
        assert plane.type == "plane-surface"

    def test_plane_location(self, plane):
        assert plane.origin.isclose((0, 0, 388.5))

    def test_plane_normal(self, plane):
        assert plane.normal.isclose((0, 0, 1))

    def test_plane_u_dir(self, plane):
        assert plane.u_dir.isclose((1, 0, 0))

    def test_plane_has_infinite_bounds(self, plane):
        assert math.isinf(plane.u_bounds[0])
        assert math.isinf(plane.u_bounds[1])
        assert math.isinf(plane.v_bounds[0])
        assert math.isinf(plane.v_bounds[1])


class TestLoop:
    @pytest.fixture(scope="class")
    def loop(self, body):
        return body.lump.shell.face.loop

    def test_loop_type(self, loop):
        assert loop.type == "loop"

    def test_cube_face_has_only_one_loop(self, loop):
        assert loop.next_loop.is_none is True

    def test_loop_references_the_parent_face(self, loop):
        assert loop.face.loop is loop

    def test_set_closed_coedges(self):
        loop = entities.Loop()
        coedges = [entities.Coedge() for _ in range(3)]
        loop.set_coedges(coedges, close=True)

        result = loop.coedges()
        assert result == coedges

    def test_set_open_coedges(self):
        loop = entities.Loop()
        coedges = [entities.Coedge() for _ in range(3)]
        loop.set_coedges(coedges, close=False)
        assert loop.coedge.prev_coedge.is_none is True

        result = loop.coedges()
        assert result == coedges


class TestCoedge:
    @pytest.fixture(scope="class")
    def coedge(self, body):
        return body.lump.shell.face.loop.coedge

    def test_co_edge_type(self, coedge):
        assert coedge.type == "coedge"

    def test_co_edges_are_organized_as_a_forward_linked_list(self, coedge):
        next = coedge.next_coedge
        co_edges = [next]
        while next is not coedge:
            next = next.next_coedge
            co_edges.append(next)
        assert len(co_edges) == 4

    def test_co_edges_are_organized_as_a_reverse_linked_list(self, coedge):
        prev = coedge.prev_coedge
        co_edges = [prev]
        while prev is not coedge:
            prev = prev.prev_coedge
            co_edges.append(prev)
        assert len(co_edges) == 4

    def test_co_edges_have_partner_co_edges_other_faces(self, coedge):
        assert coedge.partner_coedge.partner_coedge is coedge

    def test_sense_of_co_edge_is_forward(self, coedge):
        assert coedge.sense is False

    def test_co_edge_references_the_parent_loop(self, coedge):
        assert coedge.loop.coedge is coedge


class TestEdge:
    @pytest.fixture(scope="class")
    def edge(self, body):
        return body.lump.shell.face.loop.coedge.edge

    def test_edge_type(self, edge):
        assert edge.type == "edge"

    def test_edge_has_a_start_vertex(self, edge):
        assert edge.start_vertex.is_none is False

    def test_edge_has_an_end_vertex(self, edge):
        assert edge.end_vertex.is_none is False

    # start- and end parameter do not exist in ACIS-400

    def test_sense_of_edge_is_forward(self, edge):
        assert edge.sense is False

    def test_underlying_curve_of_edge(self, edge):
        assert edge.curve.type == "straight-curve"

    def test_edge_is_referenced_by_two_parent_co_edges(self, edge):
        parent = edge.coedge
        assert parent.edge is edge
        assert parent.partner_coedge.edge is edge


class TestVertex:
    @pytest.fixture(scope="class")
    def vertex(self, body):
        return body.lump.shell.face.loop.coedge.edge.start_vertex

    def test_vertex_type(self, vertex):
        assert vertex.type == "vertex"

    def test_vertex_references_parent_edge(self, vertex):
        assert vertex.edge.start_vertex is vertex


class TestPoint:
    @pytest.fixture(scope="class")
    def point(self, body):
        return body.lump.shell.face.loop.coedge.edge.start_vertex.point

    def test_point_type(self, point):
        assert point.type == "point"

    def test_point_location(self, point):
        assert point.location.isclose((388.5, -388.5, 388.5))

    def test_get_all_points(self, body):
        face = body.lump.shell.face
        vertices = set()
        while not face.is_none:
            first_coedge = face.loop.coedge
            coedge = first_coedge
            while True:
                vertices.add(coedge.edge.start_vertex.point.location)
                coedge = coedge.next_coedge
                if coedge is first_coedge:
                    break
            face = face.next_face
        assert len(vertices) == 8


@pytest.fixture(scope="module")
def prism700(prism_sat):
    return load(prism_sat)


class TestExportSat:
    def test_export_rejects_unsupported_acis_versions(self, prism700):
        with pytest.raises(ExportError):
            export_sat(prism700, version=400)

    def test_export_acis_700(self, prism700):
        data = export_sat(prism700)
        assert len(data) == 117  # includes header
        assert data[-1] == "End-of-ACIS-data "  # an extra space at the end!


class TestExportSab21800:
    def test_export_rejects_unsupported_acis_versions(self, prism700):
        with pytest.raises(ExportError):
            export_sab(prism700, version=400)

    def test_reload_records_from_acis_export(self, prism700):
        data = export_sab(prism700)
        decoder = sab.Decoder(data)
        header = decoder.read_header()
        assert header.version == 21800
        records = list(decoder.read_records())
        # 115 = excludes header
        assert len(records) == 115
        assert records[-1][0].value == "End-of-ASM-data"


def test_load_mesh_from_exported_sat_data(prism700):
    bodies = load(export_sat(prism700))
    m = mesh.mesh_from_body(bodies[0])[0]
    assert len(m.vertices) == 8
    assert len(m.faces) == 10


def test_load_mesh_from_exported_sab_data(prism700):
    bodies = load(export_sab(prism700))
    m = mesh.mesh_from_body(bodies[0])[0]
    assert len(m.vertices) == 8
    assert len(m.faces) == 10


class TestExportTransform:
    @pytest.fixture(scope="class")
    def header(self):
        header = hdr.AcisHeader()
        header.version = 700
        return header

    @pytest.fixture(scope="class")
    def sat_exporter(self, header):
        return sat.SatExporter(header)

    @pytest.fixture(scope="class")
    def sab_exporter(self, header):
        return sab.SabExporter(header)

    def test_export_sat_identity_matrix(self, sat_exporter):
        data = []
        exporter = sat.SatDataExporter(sat_exporter, data)
        t = entities.Transform()
        t.matrix = Matrix44()
        t.export(exporter)
        assert (
            " ".join(data)
            == "1 0 0 0 1 0 0 0 1 0 0 0 1 no_rotate no_reflect no_shear"
        )

    def test_export_sab_identity_matrix(self, sab_exporter):
        data = []
        exporter = sab.SabDataExporter(sab_exporter, data)
        t = entities.Transform()
        t.matrix = Matrix44()
        t.export(exporter)
        assert data[0] == (
            const.Tags.LITERAL_STR,
            "1 0 0 0 1 0 0 0 1 0 0 0 1 no_rotate no_reflect no_shear",
        )


if __name__ == "__main__":
    pytest.main([__file__])
