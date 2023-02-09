#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import is_face_normal_pointing_outwards
from ezdxf.render import forms


def test_cube_with_ccw_vertex_orientation():
    mesh = forms.cube()
    faces = list(mesh.faces_as_vertices())
    for index, face in enumerate(faces):
        assert (
            is_face_normal_pointing_outwards(faces, face) is True
        ), f"index = {index}"


def test_cube_with_clockwise_vertex_orientation():
    mesh = forms.cube()
    mesh.flip_normals()
    faces = list(mesh.faces_as_vertices())
    for index, face in enumerate(faces):
        assert (
            is_face_normal_pointing_outwards(faces, face) is False
        ), f"index = {index}"


COUNT = 11


def test_torus_with_ccw_vertex_orientation():
    mesh = forms.torus(minor_count=COUNT)
    faces = list(mesh.faces_as_vertices())
    for index, face in enumerate(faces):
        assert (
            is_face_normal_pointing_outwards(faces, face) is True
        ), f"index = {index}"


def test_torus_with_clockwise_vertex_orientation():
    mesh = forms.torus(minor_count=COUNT)
    mesh.flip_normals()
    faces = list(mesh.faces_as_vertices())
    for index, face in enumerate(faces):
        assert (
            is_face_normal_pointing_outwards(faces, face) is False
        ), f"index = {index}"


def test_flipped_cone():
    cone = forms.cone(3)
    cone.flip_normals()
    faces = list(cone.faces_as_vertices())
    for index, face in enumerate(faces):
        assert (
            is_face_normal_pointing_outwards(faces, face) is False
        ), f"index = {index}"


if __name__ == "__main__":
    pytest.main([__file__])
