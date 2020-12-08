# Copyright (c) 2018-2020 Manfred Moitzi
# License: MIT License
from ezdxf.math import PassTroughUCS, UCS, Vec3, X_AXIS, Y_AXIS, Z_AXIS


def test_u_vectors():
    ucs = PassTroughUCS()

    assert ucs.ux == X_AXIS
    assert ucs.uy == Y_AXIS
    assert ucs.uz == Z_AXIS


def test_to_wcs():
    ucs = PassTroughUCS()
    assert ucs.to_wcs((1, 2, 3)) == Vec3(1, 2, 3)
    assert ucs.to_wcs((3, 4, 5)) == Vec3(3, 4, 5)

    ucs2 = UCS()
    assert ucs.to_wcs((1, 2, 3)) == ucs2.to_wcs((1, 2, 3))
    assert ucs.to_wcs((3, 4, 5)) == ucs2.to_wcs((3, 4, 5))


def test_points_to_wcs():
    ucs = PassTroughUCS()
    assert list(ucs.points_to_wcs([(1, 2, 3), (3, 4, 5)])) == [Vec3(1, 2, 3), Vec3(3, 4, 5)]

    ucs2 = UCS()
    assert list(ucs.points_to_wcs([(1, 2, 3), (3, 4, 5)])) == list(ucs2.points_to_wcs([(1, 2, 3), (3, 4, 5)]))


def test_to_ocs():
    ucs = PassTroughUCS()
    assert ucs.to_ocs((1, 2, 3)) == Vec3(1, 2, 3)
    assert ucs.to_ocs((3, 4, 5)) == Vec3(3, 4, 5)


def test_points_to_ocs():
    ucs = PassTroughUCS()
    assert list(ucs.points_to_ocs([(1, 2, 3), (3, 4, 5)])) == [Vec3(1, 2, 3), Vec3(3, 4, 5)]


def test_from_wcs():
    ucs = PassTroughUCS()
    assert ucs.from_wcs((1, 2, 3)) == Vec3(1, 2, 3)
    assert ucs.from_wcs((3, 4, 5)) == Vec3(3, 4, 5)

    ucs2 = UCS()
    assert ucs.from_wcs((1, 2, 3)) == ucs2.from_wcs(Vec3(1, 2, 3))
    assert ucs.from_wcs((3, 4, 5)) == ucs2.from_wcs(Vec3(3, 4, 5))


def test_points_from_wcs():
    points = Vec3.list([(1, 2, 3), (3, 4, 5)])
    ucs = PassTroughUCS()
    assert list(ucs.points_from_wcs(points)) == points

    ucs2 = UCS()
    assert list(ucs.points_from_wcs(points)) == list(ucs2.points_from_wcs(points))
