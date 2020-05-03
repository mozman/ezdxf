# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import math
from ezdxf.math import Matrix44, OCS, Vector
from ezdxf.math.transformtools import transform_angle, transform_length


def test_transform_angle_without_ocs():
    extrusion = Vector(0, 0, 1)
    ocs = OCS(extrusion)
    m = Matrix44.z_rotate(math.pi / 2)
    result = transform_angle(0, ocs, extrusion, m)
    assert math.isclose(result, math.pi / 2)


def test_transform_length_without_ocs():
    ocs = OCS((0, 0, 1))
    m = Matrix44.scale(2, 3, 4)
    assert math.isclose(transform_length((2, 0, 0), ocs, m), 2*2)
    assert math.isclose(transform_length((0, 2, 0), ocs, m), 2*3)
    assert math.isclose(transform_length((0, 0, 2), ocs, m), 2*4)


if __name__ == '__main__':
    pytest.main([__file__])
