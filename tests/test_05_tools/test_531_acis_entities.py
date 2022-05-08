#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.acis import load
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

    def test_has_lump_attribute(self, body):
        assert body.lump.is_none is False

    def test_has_wire_attribute(self, body):
        assert body.wire.is_none is True


class TestLump:
    def test_first_lump(self, body):
        assert body.lump.is_none is False

    def test_lump_type(self, body):
        assert body.lump.type == "lump"

    def test_back_pointer_to_body(self, body):
        assert body.lump.body is body

    def test_has_no_next_lump(self, body):
        assert body.lump.next_lump.is_none is True

    def test_has_attribute_to_first_shell(self, body):
        assert body.lump.shell.is_none is False


class TestShell:
    @pytest.fixture(scope="class")
    def shell(self, body):
        return body.lump.shell

    def test_first_shell(self, shell):
        assert shell.is_none is False

    def test_shell_type(self, shell):
        assert shell.type == "shell"

    def test_back_pointer_to_lump(self, body, shell):
        assert shell.lump is body.lump

    def test_has_no_next_shell(self, shell):
        assert shell.next_shell.is_none is True

    def test_has_attribute_to_first_face(self, shell):
        assert shell.face.is_none is False


class TestFace:
    @pytest.fixture(scope="class")
    def face(self, body):
        return body.lump.shell.face

    def test_first_shell(self, face):
        assert face.is_none is False

    def test_face_type(self, face):
        assert face.type == "face"

    def test_back_pointer_to_shell(self, body, face):
        assert face.shell is body.lump.shell

    def test_has_a_next_face(self, face):
        assert face.next_face.is_none is False

    def test_has_attribute_surface(self, face):
        assert face.surface.type == "plane-surface"

    def test_has_attribute_to_first_loop(self, face):
        assert face.loop.is_none is False

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

    def test_loop_references_the_first_coedge(self, loop):
        assert loop.coedge.is_none is False

    def test_loop_references_the_parent_face(self, body, loop):
        assert loop.face is body.lump.shell.face


if __name__ == "__main__":
    pytest.main([__file__])
