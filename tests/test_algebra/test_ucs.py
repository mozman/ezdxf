# Copyright (c) 2018 Manfred Moitzi
# License: MIT License

from ezdxf.algebra import UCS, Vector, X_AXIS, Y_AXIS, Z_AXIS, is_close


def test_ucs_init():
    ucs = UCS()
    assert ucs.origin == (0, 0, 0)
    assert ucs.ux == (1, 0, 0)
    assert ucs.uy == (0, 1, 0)
    assert ucs.uz == (0, 0, 1)

    assert ucs.from_wcs((3, 4, 5)) == (3, 4, 5)
    assert ucs.to_wcs((5, 4, 3)) == (5, 4, 3)


def test_ucs_init_ux_uy():
    ucs = UCS(ux=X_AXIS, uy=Y_AXIS)
    assert ucs.uz == Z_AXIS
    ucs = UCS(ux=Y_AXIS, uy=X_AXIS)
    assert ucs.uz == -Z_AXIS


def test_ucs_init_ux_uz():
    ucs = UCS(ux=X_AXIS, uz=Z_AXIS)
    assert ucs.uy == Y_AXIS


def test_ucs_init_uy_uz():
    ucs = UCS(uy=Y_AXIS, uz=Z_AXIS)
    assert ucs.ux == X_AXIS
    ucs = UCS(uz=X_AXIS, uy=Z_AXIS)
    assert ucs.ux == Y_AXIS


def test_translation():
    ucs = UCS(origin=(3, 4, 5))
    assert ucs.origin == (3, 4, 5)
    assert ucs.ux == (1, 0, 0)
    assert ucs.uy == (0, 1, 0)
    assert ucs.uz == (0, 0, 1)
    assert ucs.from_wcs((3, 4, 5)) == (0, 0, 0)
    assert ucs.to_wcs((1, 1, 1)) == (4, 5, 6)


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


def test_arbitrary_ucs():
    origin = Vector(3, 3, 3)
    ux = Vector(1, 2, 0)
    def_point_in_xy_plane = Vector(3, 10, 4)
    uz = ux.cross(def_point_in_xy_plane - origin)
    ucs = UCS(origin=origin, ux=ux, uz=uz)
    def_point_in_ucs = ucs.from_wcs(def_point_in_xy_plane)
    assert def_point_in_ucs.z == 0
    assert ucs.to_wcs(def_point_in_ucs) == def_point_in_xy_plane
    assert ucs.is_cartesian is True


def test_constructor_functions():
    # does not check the math, because tis would just duplicate the implementation code
    origin = (3, 3, 3)
    axis = (1, 0, -1)
    def_point = (3, 10, 4)
    ucs = UCS.from_x_axis_and_point_in_xy(origin, axis=axis, point=def_point)
    assert ucs.is_cartesian
    assert is_close(ucs.from_wcs(def_point).z, 0)

    ucs = UCS.from_x_axis_and_point_in_xz(origin, axis=axis, point=def_point)
    assert ucs.is_cartesian
    assert is_close(ucs.from_wcs(def_point).y, 0)

    ucs = UCS.from_y_axis_and_point_in_xy(origin, axis=axis, point=def_point)
    assert ucs.is_cartesian
    assert is_close(ucs.from_wcs(def_point).z, 0)

    ucs = UCS.from_y_axis_and_point_in_yz(origin, axis=axis, point=def_point)
    assert ucs.is_cartesian
    assert is_close(ucs.from_wcs(def_point).x, 0)

    ucs = UCS.from_z_axis_and_point_in_xz(origin, axis=axis, point=def_point)
    assert ucs.is_cartesian
    assert is_close(ucs.from_wcs(def_point).y, 0)

    ucs = UCS.from_z_axis_and_point_in_yz(origin, axis=axis, point=def_point)
    assert ucs.is_cartesian
    assert is_close(ucs.from_wcs(def_point).x, 0)
