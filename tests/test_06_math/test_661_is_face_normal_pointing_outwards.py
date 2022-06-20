#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import is_face_normal_pointing_outwards
from ezdxf.render import forms


def test_cube_with_ccw_vertex_orientation():
    cube = forms.cube()
    faces = list(cube.faces_as_vertices())
    for face in faces:
        assert is_face_normal_pointing_outwards(faces, face) is True


def test_cube_with_clockwise_vertex_orientation():
    cube = forms.cube()
    cube.flip_normals()
    faces = list(cube.faces_as_vertices())
    for face in faces:
        assert is_face_normal_pointing_outwards(faces, face) is False


if __name__ == "__main__":
    pytest.main([__file__])
