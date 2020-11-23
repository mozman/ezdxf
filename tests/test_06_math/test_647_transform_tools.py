# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import math
from ezdxf.math import Matrix44, Vec3
from ezdxf.math.transformtools import OCSTransform


def test_transform_angle_without_ocs():
    ocs = OCSTransform(Vec3(0, 0, 1), Matrix44.z_rotate(math.pi / 2))
    assert math.isclose(ocs.transform_angle(0), math.pi / 2)


def test_transform_length_without_ocs():
    ocs = OCSTransform(Vec3(0, 0, 1), Matrix44.scale(2, 3, 4))
    assert math.isclose(ocs.transform_length((2, 0, 0)), 2*2)
    assert math.isclose(ocs.transform_length((0, 2, 0)), 2*3)
    assert math.isclose(ocs.transform_length((0, 0, 2)), 2*4)


if __name__ == '__main__':
    pytest.main([__file__])
