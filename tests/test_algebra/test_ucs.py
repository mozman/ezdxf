# Copyright (c) 2018 Manfred Moitzi
# License: MIT License

from ezdxf.algebra import UCS, Vector


def test_ucs_init():
    ucs = UCS()
    assert ucs.origin == (0, 0, 0)
    assert ucs.ux == (1, 0, 0)
    assert ucs.uy == (0, 1, 0)
    assert ucs.uz == (0, 0, 1)

    assert ucs.wcs_to_ucs((3, 4, 5)) == (3, 4, 5)
    assert ucs.ucs_to_wcs((5, 4, 3)) == (5, 4, 3)


def test_translation():
    ucs = UCS(origin=(3, 4, 5))
    assert ucs.origin == (3, 4, 5)
    assert ucs.ux == (1, 0, 0)
    assert ucs.uy == (0, 1, 0)
    assert ucs.uz == (0, 0, 1)
    assert ucs.wcs_to_ucs((3, 4, 5)) == (0, 0, 0)
    assert ucs.ucs_to_wcs((1, 1, 1)) == (4, 5, 6)


def test_rotation():
    # normalization is not necessary
    ux = Vector(1, 2, 0)
    # only cartesian coord systems work
    uy = ux.rot_z_deg(90)
    ucs = UCS(ux=ux, uy=uy)
    assert ucs.ux == ux.normalize()
    assert ucs.uy == uy.normalize()
    assert ucs.uz == (0, 0, 1)
    assert ucs.is_cartesian is True


def test_none_cartesian():
    ucs = UCS(ux=(1, 2), uy=(0, 2))
    assert ucs.is_cartesian is False
