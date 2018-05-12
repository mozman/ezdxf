# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.modern.mesh import create_vertex_array, create_face_list, create_edge_array, create_crease_array
from ezdxf.modern.mesh import tag_processor, face_to_array
from . test_mesh import MESH


@pytest.fixture
def mesh():
    tags = ExtendedTags.from_text(MESH)
    return tags.get_subclass('AcDbSubDMesh')


def mesh_geometric_data():
    with mesh.edit_data() as mesh_data:
        assert 56 == len(mesh_data.vertices)
        assert 54 == len(mesh_data.faces)
        assert 108 == len(mesh_data.edges)
        assert 108 == len(mesh_data.edge_crease_values)


def test_create_vertex_array(mesh):
    start_index = mesh.tag_index(92) + 1
    vertices = create_vertex_array(mesh, start_index)
    assert len(vertices) == 56

    tags = list(vertices.dxftags())
    assert tags[0].code == 92
    assert tags[0].value == 56
    assert len(tags) == 57


def test_create_face_list(mesh):
    start_index = mesh.tag_index(93) + 1
    faces = create_face_list(mesh, start_index)
    assert len(faces) == 54

    tags = list(faces.dxftags())
    assert tags[0].code == 93
    assert tags[0].value == 270
    assert faces.tag_count() == 270
    # tag count + counter
    assert len(tags) == 271


def test_create_edge_array(mesh):
    start_index = mesh.tag_index(94) + 1
    edges = create_edge_array(mesh, start_index)
    assert len(edges) == 108

    tags = list(edges.dxftags())
    assert tags[0].code == 94
    assert tags[0].value == 108
    # always two tags per edge + counter
    assert len(tags) == 217


def test_create_crease_array(mesh):
    start_index = mesh.tag_index(95) + 1
    creases = create_crease_array(mesh, start_index)

    assert len(creases) == 108

    tags = list(creases.dxftags())
    assert tags[0].code == 95
    assert tags[0].value == 108
    # always one tag per crease value + counter
    assert len(tags) == 109


def test_tags_processor():
    tags = ExtendedTags.from_text(MESH)
    mesh_tags = tags.get_subclass('AcDbSubDMesh')
    assert len(mesh_tags) == 659
    tag_processor(tags)
    assert mesh_tags[-1] == (90, 0)
    vertices = mesh_tags.get_first_tag(-92)
    assert len(vertices) == 56
    faces = mesh_tags.get_first_tag(-93)
    assert len(faces) == 54
    edges = mesh_tags.get_first_tag(-94)
    assert len(edges) == 108
    creases = mesh_tags.get_first_tag(-95)
    assert len(creases) == 108
    assert len(mesh_tags) == 9


def test_tags_processor_empty_mesh():
    from ezdxf.modern.mesh import _MESH_TPL
    tags = ExtendedTags.from_text(_MESH_TPL)
    tag_processor(tags)
    mesh_tags = tags.get_subclass('AcDbSubDMesh')
    assert mesh_tags[-1] == (90, 0)
    vertices = mesh_tags.get_first_tag(-92)
    assert len(vertices) == 0
    faces = mesh_tags.get_first_tag(-93)
    assert len(faces) == 0
    edges = mesh_tags.get_first_tag(-94)
    assert len(edges) == 0
    creases = mesh_tags.get_first_tag(-95)
    assert len(creases) == 0
    assert len(mesh_tags) == 9


def test_face_indices_as_array():
    a = face_to_array([0, 1, 2, 3])
    assert a.typecode == 'B'

    a = face_to_array([0, 1, 2, 512])
    assert a.typecode == 'I'

    a = face_to_array([0, 1, 2, 100000])
    assert a.typecode == 'L'

