# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf.algebra import Matrix44
import pytest

IDENTITY_MATRIX = list(list(Matrix44()))

MATRIX_CHECK = [
    1, 2, 3, 4,
    5, 6, 7, 8,
    9, 10, 11, 12,
    13, 14, 15, 16
]


@pytest.fixture(scope='module')
def msp():
    dwg = ezdxf.new('R2007')
    return dwg.modelspace()


def test_surface(msp):
    surface = msp.add_surface()
    assert surface.dxftype() == 'SURFACE'
    # ACIS data is tested in test_body()
    assert list(surface.get_acis_data()) == []


def test_extruded_surface(msp):
    surface = msp.add_extruded_surface()
    assert surface.dxftype() == 'EXTRUDEDSURFACE'
    assert list(surface.get_acis_data()) == []

    matrix = surface.get_transformation_matrix_extruded_entity()
    assert list(matrix) == IDENTITY_MATRIX

    matrix = surface.get_sweep_entity_transformation_matrix()
    assert list(matrix) == IDENTITY_MATRIX

    matrix = surface.get_path_entity_transformation_matrix()
    assert list(matrix) == IDENTITY_MATRIX

    surface.set_transformation_matrix_extruded_entity(MATRIX_CHECK)
    assert list(surface.get_transformation_matrix_extruded_entity()) == MATRIX_CHECK

    with pytest.raises(ezdxf.DXFValueError):
        surface.set_transformation_matrix_extruded_entity(MATRIX_CHECK[:-1])


def test_lofted_surface(msp):
    surface = msp.add_lofted_surface()
    assert surface.dxftype() == 'LOFTEDSURFACE'
    assert list(surface.get_acis_data()) == []

    matrix = surface.get_transformation_matrix_lofted_entity()
    assert list(matrix) == IDENTITY_MATRIX


def test_swept_surface(msp):
    surface = msp.add_swept_surface()
    assert surface.dxftype() == 'SWEPTSURFACE'
    assert list(surface.get_acis_data()) == []


def test_revolved_surface(msp):
    surface = msp.add_revolved_surface()
    assert surface.dxftype() == 'REVOLVEDSURFACE'
    assert list(surface.get_acis_data()) == []

    matrix = surface.get_transformation_matrix_revolved_entity()
    assert list(matrix) == IDENTITY_MATRIX
