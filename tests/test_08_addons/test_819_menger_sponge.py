#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest

from ezdxf.addons import MengerSponge


@pytest.fixture(scope="module")
def mesh():
    return MengerSponge().mesh()


def test_euler_characteristic_for_menger_sponge(mesh):
    """The euler characteristic does not work for non-convex meshes."""
    diag = mesh.diagnose()
    assert diag.euler_characteristic == -8


def test_edge_balance_for_menger_sponge(mesh):
    """ The is_edge_balance_broken property is not reliable for concave meshes
    each edge connects two faces
    """
    diag = mesh.diagnose()
    assert diag.is_edge_balance_broken is False


def test_menger_sponge_is_non_manifold(mesh):
    diag = mesh.diagnose()
    assert diag.is_manifold is True


def test_menger_sponge_face_count(mesh):
    assert len(mesh.faces) == 72


def test_menger_sponge_edge_count(mesh):
    assert len(mesh.vertices) == 64


if __name__ == '__main__':
    pytest.main([__file__])
