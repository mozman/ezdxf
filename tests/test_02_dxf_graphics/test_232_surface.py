# Copyright (c) 2018-2019 Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf.math import Matrix44
import pytest

IDENTITY_MATRIX = list(list(Matrix44()))

MATRIX_CHECK = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]


@pytest.fixture(scope="module")
def msp():
    doc = ezdxf.new("R2007")
    return doc.modelspace()


def test_surface(msp):
    surface = msp.add_surface()
    assert surface.dxftype() == "SURFACE"
    # ACIS data is tested in test_body()
    assert len(surface.sat) == 0


def test_extruded_surface(msp):
    surface = msp.add_extruded_surface()
    assert surface.dxftype() == "EXTRUDEDSURFACE"
    assert len(surface.sat) == 0

    matrix = surface.transformation_matrix_extruded_entity
    assert list(matrix) == IDENTITY_MATRIX

    matrix = surface.sweep_entity_transformation_matrix
    assert list(matrix) == IDENTITY_MATRIX

    matrix = surface.path_entity_transformation_matrix
    assert list(matrix) == IDENTITY_MATRIX

    surface.transformation_matrix_extruded_entity = Matrix44(MATRIX_CHECK)
    assert list(surface.transformation_matrix_extruded_entity) == MATRIX_CHECK


def test_lofted_surface(msp):
    surface = msp.add_lofted_surface()
    assert surface.dxftype() == "LOFTEDSURFACE"
    assert len(surface.sat) == 0

    matrix = surface.transformation_matrix_lofted_entity
    assert list(matrix) == IDENTITY_MATRIX


def test_swept_surface(msp):
    surface = msp.add_swept_surface()
    assert surface.dxftype() == "SWEPTSURFACE"
    assert len(surface.sat) == 0


def test_revolved_surface(msp):
    surface = msp.add_revolved_surface()
    assert surface.dxftype() == "REVOLVEDSURFACE"
    assert len(surface.sat) == 0

    matrix = surface.transformation_matrix_revolved_entity
    assert list(matrix) == IDENTITY_MATRIX
